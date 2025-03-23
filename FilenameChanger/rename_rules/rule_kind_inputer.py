# FilenameChanger/rename_rules/rule_kind_inputer.py
from FilenameChanger.rename_rules.rule_manager import *

"""
此模块将重命名规则按种类区分输入
"""


def input_new_rule(config_path):
    """
    功能：提示用户输入规则
    :param config_path: 配置文件路径
    """

    class TypeLegalityError(Exception):
        def __init__(self, value):
            self.value = value
            self.__class__.__name__ = '【规则种类合法性异常】' + self.__class__.__name__

    # 验证规则种类合法性
    legal_type = [1]  # 合法的种类值列表
    try:
        print('【1】交换特定符号前后内容')
        rule_type = int(input('请选择规则类型：'))
        if rule_type not in legal_type:
            raise TypeLegalityError
    except TypeLegalityError as e:
        print(e.__cause__.__name__, '已触发，错误的规则种类：', e.value, sep='')

    if rule_type == 1:
        input_mode_1(config_path)
    elif rule_type == 2:
        pass


def input_mode_1(config_path):
    """
    规则种类：拆分特定分隔符前后的文件名并交换
    :param config_path: 配置文件路径
    """
    split_rule = {}  # 创建文件名分割规则字典
    split_rule['type'] = 1
    split_rule['rule_name'] = input('请输入规则名称：')
    split_rule['desc'] = input('请输入规则描述：')
    split_rule['split_char'] = input('请输入分隔符：')

    save_new_rule(split_rule, config_path)  # 保存输入的规则
