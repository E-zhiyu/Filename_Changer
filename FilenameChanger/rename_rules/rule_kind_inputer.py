# FilenameChanger/rename_rules/rule_kind_inputer.py
from itertools import cycle

from FilenameChanger.rename_rules.rule_manager import *
from FilenameChanger.log.log_recorder import *

"""
此模块将重命名规则按种类区分输入
"""


def set_new_rule(config_path):
    """
    功能：提示用户输入规则
    参数 config_path：配置文件路径
    """
    all_rule_types = """
【1】交换特定符号前后内容
    """
    print('规则写入'.center(42, '—'))
    print('以下为所有规则类型')
    print(all_rule_types)

    cycle = True
    while cycle:
        try:
            rule_type = int(input('请选择：'))
            cycle = False
        except ValueError:  # 防止没有输入
            print('请选择一个规则类型！')

    logger.info(f'用户选择规则类型{rule_type}')
    if rule_type == 1:
        input_mode_1(config_path)
    else:
        print('【选择错误】你选择了一个不存在的操作！')


def input_mode_1(config_path):
    """
    功能：输入规则并保存
    规则种类一：拆分特定分隔符前后的文件名并交换
    参数 config_path：配置文件路径
    """
    all_rules = load_config(config_path)  # 获取现有的规则

    split_rule = {}  # 创建文件名分割规则字典
    split_rule['type'] = 1
    split_rule['rule_name'] = input('请输入规则名称：')
    logger.info(f'输入规则名称：“{split_rule["rule_name"]}”')
    split_rule['desc'] = input('请输入规则描述：')
    logger.info(f'输入规则描述：“{split_rule["desc"]}”')
    split_rule['split_char'] = input('请输入分隔符：')
    logger.info(f'输入分隔符：“{split_rule["split_char"]}”')

    save_new_rule(all_rules, split_rule, config_path)  # 保存输入的规则
