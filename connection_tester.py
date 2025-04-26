
#connection_tester.py

import logging
from ssh_manager import SSHManager
from config_manager import load_config

def test_jump_connection(config_path: str, timeout=10):
    """測試 jump server 連線流程"""
    config = load_config(config_path)
    with SSHManager(config, timeout=timeout) as ssh_manager:
        total = len(config.get("jump_servers", [])) + 1
        logging.info(f"[✔] 測試通過：{total} 層連線成功")
