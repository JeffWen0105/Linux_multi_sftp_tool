# config_manager.py

import os
import yaml
import sys
import logging

def load_config(config_file):
    """載入並驗證檔案"""
    if not os.path.exists(config_file):
        create_default_config(config_file)
        logging.error(f"[!] AUTH 檔案 {config_file} 不存在，已自動產生。請編輯後再次執行。")
        raise FileNotFoundError(f"AUTH 檔案 {config_file} 不存在")
    try:
        with open(config_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        validate_config(config)
        return config
    except yaml.YAMLError as e:
        logging.error(f"[X] AUTH 檔案格式錯誤：{e}")
        raise ValueError("YAML 格式錯誤")

def create_default_config(config_file):
    """Default AUTH 檔案"""
    default = {
        'jump_servers': [
            {'host': '192.168.50.200', 'port': 22, 'username': 'example', 'password': 'example'},
            {'host': '192.168.50.201', 'port': 22, 'username': 'example', 'password': ''},
        ],
        'target': {
            'host': 'target.example.com', 'port': 22, 'username': 'targetuser', 'password': ''
        }
    }
    with open(config_file, 'w', encoding="utf-8") as f:
        yaml.dump(default, f)

def validate_config(config):
    """驗證 AUTH 檔案"""
    if not config.get('target', {}).get('host'):
        raise ValueError("[X] AUTH 檔案缺少 target.host")
    if not config.get('target', {}).get('username'):
        raise ValueError("[X] AUTH 檔案缺少 target.username")
    for i, jump in enumerate(config.get('jump_servers', [])):
        if not jump.get('host'):
            raise ValueError(f"[X] 第 {i+1} 個 jumpserver 缺少 host")
        if not jump.get('username'):
            raise ValueError(f"[X] 第 {i+1} 個 jumpserver 缺少 username")
