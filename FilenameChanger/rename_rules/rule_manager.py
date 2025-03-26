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
    except FileNotFoundError:
        return None


def analysis_rules(rule, old_names):
    """
    功能：解析重命名规则并分割文件名
    返回：被分割文件名的前后部分
    """
    split_char = rule['split_char']
    names = []  # 文件名列表
    exts = []  # 扩展名列表
    for file in old_names:
        signal_name, signal_ext = os.path.splitext(file)  # 分离文件名和扩展名
        names.append(signal_name)
        exts.append(signal_ext)

    front = []  # 前半部分文件名
    behind = []  # 后半部分文件名
    for signal_name in names:
        parts = signal_name.split(split_char, maxsplit=1)  # 将拆分的两个部分存放至列表parts中
        f = parts[0]
        b = parts[1] if len(parts) > 1 else ''  # 默认第二部分为空，用于处理无法拆分的文件名
        front.append(f)
        behind.append(b)

    return zip(front, behind, exts)


def save_new_rule(new_rule, config_path):
    """
    功能：保存用户输入的规则
    :param new_rule:新规则列表
    :param config_path:规则文件路径
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_rule, f, ensure_ascii=False, indent=4)
        print('规则写入成功！')
    except FileNotFoundError:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_rule, f, ensure_ascii=False, indent=4)
        print('规则写入成功！')
