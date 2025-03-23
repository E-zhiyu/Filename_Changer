# config/rule_manager.py
import json
import os
from os.path import split
from pydoc import describe

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
        f, b = i.split(split_char, 1)  # 以第一个出现的分隔符为界限分割文件名
        front.append(f)
        behind.append(b)

    zipped_names = zip(front, behind, exts)  # 内容为[(front,behind,exts),...]
    return zipped_names


def save_new_rule(new_rule, config_path):
    """
    :param new_rule:新规则列表
    :param config_path:规则文件路径
    """
    json.dump(new_rule, open(config_path, 'w'), indent=4)


def input_new_rule(config_path):
    """
    功能：提示用户输入规则
    :param config_path: 配置文件路径
    """
    print('【1】交换特定符号前后内容')
    type = int(input('请选择规则类型：'))
    if type == 1:
        split_rule = {}  # 创建文件名分割规则字典
        split_rule['type'] = type
        split_rule['rule_name'] = input('请输入规则名称：')
        split_rule['desc'] = input('请输入规则描述：')
        split_rule['split_char'] = input('请输入分隔符：')

        save_new_rule(split_rule, config_path)  # 保存输入的规则
