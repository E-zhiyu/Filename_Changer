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
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as e:
        print(f'【错误：文件不存在】\n无法在 {config_path} 中找到配置文件！')


def analysis_rules(rule, old_names):
    """
    功能：解析重命名规则并分割文件名
    返回：被分割文件名的前后部分
    """
    split_char = rule['split_char']
    names = []  # 文件名列表
    exts = []  # 扩展名列表
    for i in range(len(old_names)):
        signal_name, signal_ext = os.path.splitext(old_names[i])  # 分离文件名和扩展名
        names.append(signal_name)
        exts.append(signal_ext)

    front = []  # 前半部分文件名
    behind = []  # 后半部分文件名
    for i in names:
        part = i.split(split_char, maxsplit=1)  # 确保至多拆分成两个部分
        f = part[0]
        b = part[1] if len(part) > 1 else ''  # 处理没有第二部分的情况
        front.append(f)
        behind.append(b)

    zipped_names = zip(front, behind, exts)  # 内容为[(front,behind,exts),...]
    return zipped_names


def save_new_rule(new_rule, config_path):
    """
    功能：保存用户输入的规则
    :param new_rule:新规则列表
    :param config_path:规则文件路径
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_rule, f, ensure_ascii=False, indent=4)
    except FileNotFoundError as e:
        print(f'【错误：文件不存在】\n无法在 {config_path} 中找到配置文件！')
