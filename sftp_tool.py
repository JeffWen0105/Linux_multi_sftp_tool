#!/usr/bin/env python3
# sftp_tool.py

import argparse
import sys
import os
from config_manager import load_config
from ssh_manager import SSHManager
from file_transfer import FileTransfer
from utils import setup_logging
from connection_tester import test_jump_connection
import logging

def parse_args():
    parser = argparse.ArgumentParser(description='HowHow JumpServer SFTP 工具 - v2.1')
    parser.add_argument('mode', choices=['upload', 'download', 'test'], help='模式')
    parser.add_argument('path1', nargs='?', help='local_path（upload）或 remote_path（download）')
    parser.add_argument('path2', nargs='?', help='remote_path（upload）或 local_path（download）')
    parser.add_argument('--config', default='config.yaml', help='指定 AUTH 檔案路徑')
    parser.add_argument('--force', action='store_true', help='強制取代已有檔案')
    parser.add_argument('--debug', action='store_true', help='Debug Mode')
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(debug=args.debug)

    logging.info(f"[Orz..] Welcome To Use JumpServer Sftp Tool ( º﹃º ) Power By HowHow  - v2.0")
    try:
        config = load_config(args.config)
        ssh_manager = SSHManager(config, timeout=10)

        if args.mode == 'test':
            test_jump_connection(args.config)
            return

        if not args.path1 or not args.path2:
            sys.exit("[X] 請提供必要的檔案路徑參數")

        local_path = args.path1 if args.mode == 'upload' else args.path2
        remote_path = args.path2 if args.mode == 'upload' else args.path1

        with ssh_manager as manager:
            file_transfer = FileTransfer(manager.get_sftp(), force_overwrite=args.force)
            if args.mode == 'upload':
                if os.path.isdir(local_path):
                    file_transfer.upload_dir(local_path, remote_path)
                else:
                    file_transfer.upload(local_path, remote_path)
            else:
                if file_transfer._remote_isdir(remote_path):
                    file_transfer.download_dir(remote_path, local_path)
                else:
                    file_transfer.download(remote_path, local_path)


    except KeyboardInterrupt:
        sys.exit("\n[!] 使用者中斷操作，掰掰~~")
    except Exception as e:
        sys.exit(f"[X] 發生錯誤：{e}")

if __name__ == '__main__':
    main()