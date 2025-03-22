# config/config_manager.py
import json

"""
配置文件读写模块
"""


def load_config(config_path):
    """加载配置文件"""
    with open(config_path, 'r') as f:
        return json.load(f)


def save_config(config):
    """保存配置文件"""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
