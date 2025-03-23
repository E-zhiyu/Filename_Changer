# file_operations/file_utils.py
from FilenameChanger.rename_rules.rule_manager import *

from FilenameChanger.rename_rules.rule_manager import analysis_rules

"""
文件操作模块
"""


def get_files_in_directory(directory):
    """
    :param directory: 目标路径
    :return: 旧文件名列表
    """
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def rename_files(directory, old_name, new_name):
    """重命名文件"""
    os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))


def generate_new_name(rule, old_names):
    """
    功能：根据已加载的规则生成新文件名
    返回：新文件名列表
    """
    split_char = rule['split_char']
    zipped_names = analysis_rules(rule, old_names)
    new_names = []
    for i in zipped_names:
        f, b, e = i

        # 去除前后空格
        if f[0] == ' ':
            f = f[1:]
        if f[-1] == ' ':
            f = f[:-1]
        if b[0] == ' ':
            b = b[1:]
        if b[-1] == ' ':
            b = b[:-1]

        new = b + ' ' + split_char + ' ' + f + e  # 新文件名为"behind+空格+split_char+空格+front+ext"
        new_names.append(new)

    return new_names
