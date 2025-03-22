# config/rule_manager.py
import json
import os

"""
规则文件模块：控制所有有关命名规则文件的操作
"""


def load_config(config_path):
    """
    功能：加载配置文件

    返回：json文件内容
    """
    with open(config_path, 'r') as f:
        return json.load(f)


def save_config(config):
    """保存配置文件"""
    with open('rename_rules.json', 'w') as f:
        json.dump(config, f, indent=4)


def analysis_rules(rule, old_names):
    """
    功能：解析重命名规则并分割文件名

    返回：被分割文件名的前后部分
    """
    slip_char = rule['slip_char']
    names = []  # 文件名列表
    exts = []  # 扩展名列表
    for i in range(len(old_names)):
        names, exts = os.path.splitext(old_names[i])  # 分离文件名和扩展名

    front = []  # 分隔符前的部分文件名
    behind = []  # 分隔符后的部分文件名
    for i in range(len(names)):
        f, b = names[i].split(slip_char, 1)  # 以第一个出现的分隔符为界限分割文件名
        front.append(f)
        behind.append(b)

    zipped_names = zip(front, behind, exts)  # 内容为[(front,behind,exts),...]
    return zipped_names
