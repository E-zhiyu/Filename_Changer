# rename_rules/rule_manager.py
import json
import os
from FilenameChanger.log.log_recorder import *

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
            logger.info('规则配置加载成功')
            return json.load(f)
    except FileNotFoundError:
        logger.info('未找到配置文件，正在创建并初始化……')
        init_json(config_path)
        with open(config_path, 'r', encoding='utf-8') as f:
            logger.info('成功读取初始化的规则配置')
            return json.load(f)


def analysis_rules(all_rules, old_names):
    """
    功能：解析重命名规则并分割文件名
    返回：被分割文件名的前后部分
    """
    selected_index = all_rules['selected_index']  # 获取被选区的规则的索引
    if all_rules['rules'][selected_index]['type'] == 1:
        split_char = get_the_function(all_rules)
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


def save_new_rule(all_rules, new_rule, config_path):
    """
    功能：保存用户输入的规则
    :param new_rule:新规则列表
    :param config_path:规则文件路径
    """
    all_rules['num'] += 1
    all_rules['rules'].append(new_rule)  # 将新规则并入现有的规则

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(all_rules, f, ensure_ascii=False, indent=4)
    print('新规则已成功保存！')
    logger.info('新规则保存成功')


def init_json(config_path):
    """
    功能：在没有规则文件或者规则文件为空的前提下初始化规则文件
    """
    inited_rules = {'num': 0, 'selected_index': 0, 'rules': []}
    os.makedirs(os.path.dirname(config_path), exist_ok=True)  # 先创建规则文件目录
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(inited_rules, f, ensure_ascii=False, indent=4)

    logger.info('规则文件初始化成功')


def get_the_function(all_rules):
    """
    功能：判断规则种类
    :param all_rules:规则文件的所有内容
    返回：关键功能参数
    """

    selected_index = all_rules['selected_index']
    rule_type = all_rules['rules'][selected_index]['type']

    # 判断规则类型
    logger.info('开始判断规则类型')
    if rule_type == 1:
        logger.info('已返回规则类型一的分隔符')
        return all_rules['rules'][selected_index]['split_char']
