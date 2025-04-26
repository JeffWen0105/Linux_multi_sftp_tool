import paramiko
import getpass
import sys
import logging
from contextlib import contextmanager

class SSHManager:
    def __init__(self, config, timeout=10):
        self.config = config
        self.timeout = timeout
        self.clients = []
        self.sftp = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """create jump rolemap"""
        proxy = None
        for i, jump in enumerate(self.config.get('jump_servers', [])):
            client = self._connect_single(jump, proxy, f"Jump {i+1} ({jump['host']})")
            proxy = client.get_transport().open_channel(
                'direct-tcpip',
                (self.config['target']['host'], self.config['target'].get('port', 22)),
                ('127.0.0.1', 0)
            )
            self.clients.append(client)

        target = self.config['target']
        target_client = self._connect_single(target, proxy, f"Target ({target['host']})")
        self.clients.append(target_client)
        self.sftp = target_client.open_sftp()

    def _connect_single(self, server, proxy, label):
        """connect server"""
        password = server.get('password') or ask_password(server['username'] , label)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                server['host'],
                port=server.get('port', 22),
                username=server['username'],
                password=password or None,
                sock=proxy,
                timeout=self.timeout,
          #      key_filename=server.get('key_filename')
            )
            logging.info(f"[+] 成功 connect {label}")
            return client
        except Exception as e:
            sys.exit(f"[X] 無法 connect {label}：{e}")

    def test_connection(self):
        """測試 connect"""
        self.connect()
        logging.info(f"[*] 測試通過：{len(self.clients)} 層連線成功")
        self.close()

    def get_sftp(self):
        return self.sftp

    def close(self):
        if self.sftp:
            self.sftp.close()
        for client in self.clients:
            client.close()
        self.clients.clear()
        logging.debug("[*] 所有連線已關閉 BYE BYE ~~~~~")

def ask_password(user,label):
    try:
        return getpass.getpass(f"請輸入 {user}@{label} 密碼：")
    except KeyboardInterrupt:
        sys.exit("\n[X] BYE BYE ~")