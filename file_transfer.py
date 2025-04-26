import os
import sys
import stat
import time
import colorama

import logging
from math import ceil

class FileTransfer:
    """處理檔案上傳和下載"""
    def __init__(self, sftp, chunk_size=32768, force_overwrite=False):
        self.sftp = sftp
        self.chunk_size = chunk_size
        self.force_overwrite = force_overwrite
        colorama.init()

    def upload(self, local_path, remote_path):
        """上傳"""
        if not os.path.isfile(local_path):
            sys.exit(f"[X] {local_path} 檔案不存在 ... >_<")
        
        try:
            if not self.force_overwrite and self._remote_file_exists(remote_path):
                sys.exit(f"[X] Remote 檔案 {remote_path} 已存在，請使用 --force 強制取代")
            
            filesize = os.path.getsize(local_path)
            with open(local_path, 'rb') as f:
                with self.sftp.file(remote_path, 'wb') as remote:
                    self._transfer(f, remote, filesize, os.path.basename(local_path))
            logging.info(f"[✔] 上傳完成：{remote_path}")
        except Exception as e:
            sys.exit(f"[X] 上傳失敗：{e}")

    def download(self, remote_path, local_path):
        """下載"""
        try:
            if not self._remote_file_exists(remote_path):
                sys.exit(f"[X] Remote  檔案 {remote_path} 不存在")
            
            if os.path.isdir(local_path):
                local_path = os.path.join(local_path, os.path.basename(remote_path))
            
            if not self.force_overwrite and os.path.exists(local_path):
                sys.exit(f"[X] Local 檔案 {local_path} 已存在，請使用 --force 強制取代")
            
            filesize = self.sftp.stat(remote_path).st_size
            with self.sftp.file(remote_path, 'rb') as remote:
                remote.prefetch()
                with open(local_path, 'wb') as f:
                    self._transfer(remote, f, filesize, os.path.basename(remote_path))
            logging.info(f"[✔] 下載完成：{local_path}")
        except Exception as e:
            sys.exit(f"[X] 下載失敗：{e}")


    def upload_dir(self, local_dir, remote_dir):
        if not os.path.isdir(local_dir):
            sys.exit(f"[X] {local_dir} 不是目錄")

        self._mkdir_p(remote_dir)

        for root, dirs, files in os.walk(local_dir):
            rel_path = os.path.relpath(root, local_dir)
            remote_path = remote_dir if rel_path == '.' else self._join(remote_dir, rel_path)
            self._mkdir_p(remote_path)
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = self._join(remote_path, file)
                self.upload(local_file, remote_file)

    def download_dir(self, remote_dir, local_dir):
        if not self._remote_isdir(remote_dir):
            sys.exit(f"[X] {remote_dir} 不是遠端目錄")

        os.makedirs(local_dir, exist_ok=True)

        for item in self.sftp.listdir_attr(remote_dir):
            remote_path = self._join(remote_dir, item.filename)
            local_path = os.path.join(local_dir, item.filename)
            if stat.S_ISDIR(item.st_mode):
                self.download_dir(remote_path, local_path)
            else:
                self.download(remote_path, local_path)

    def _mkdir_p(self, remote_path):
        """模擬 mkdir -p"""
        parts = remote_path.strip('/').split('/')
        current = ''
        for part in parts:
            current += '/' + part
            try:
                self.sftp.stat(current)
            except IOError:
                self.sftp.mkdir(current)

    def _remote_isdir(self, path):
        try:
            return stat.S_ISDIR(self.sftp.stat(path).st_mode)
        except IOError:
            return False

    def _join(self, a, b):
        return a.rstrip('/') + '/' + b.lstrip('/')



    def _remote_file_exists(self, remote_path):
        try:
            self.sftp.stat(remote_path)
            return True
        except IOError:
            return False

    def _transfer(self, source, dest, filesize, filename):
        transferred = 0
        last_time = start_time = time.time()
        last_bytes = 0

        while transferred < filesize:
            chunk = source.read(self.chunk_size)
            if not chunk:
                break
            dest.write(chunk)
            transferred += len(chunk)

            now = time.time()
            elapsed = now - last_time
            if elapsed >= 1:
                speed = (transferred - last_bytes) / elapsed  # bytes/sec
                eta = self._calculate_eta(transferred, filesize, now - start_time)
                self._show_progress_bar(transferred, filesize, filename, speed, eta)
                last_time = now
                last_bytes = transferred

        # 最後一次顯示
        self._show_progress_bar(transferred, filesize, filename, 0, 0)
        print()

    def _calculate_eta(self, transferred, total, elapsed):
        """計算 ETA"""
        if transferred == 0 or elapsed == 0:
            return 0
        speed = transferred / elapsed
        remaining = total - transferred
        eta = int(remaining / speed)
        return eta

    def _show_progress_bar(self, transferred, total, filename, speed_bytes=0, eta_secs=0):
        from colorama import Fore, Style
        width = 30
        percent = int(transferred * 100 / total) if total else 0
        filled = ceil(width * percent / 100)
        bar = '█' * filled + '-' * (width - filled)

        # 格式化速度
        speed_str = ""
        if speed_bytes > 0:
            kb = speed_bytes / 1024
            mb = kb / 1024
            speed_str = f"{mb:.2f} MB/s" if mb >= 1 else f"{kb:.1f} KB/s"

        # 格式化 ETA
        eta_str = ""
        if eta_secs > 0:
            mins, secs = divmod(eta_secs, 60)
            eta_str = f"ETA: {mins:02d}:{secs:02d}"

        color = Fore.GREEN if percent == 100 else Fore.CYAN
        reset = Style.RESET_ALL
        print(
            f"\r{color}[{bar}] {percent:3d}%  {filename}  {speed_str}  {eta_str}{reset}",
            end='',
            flush=True
        )
