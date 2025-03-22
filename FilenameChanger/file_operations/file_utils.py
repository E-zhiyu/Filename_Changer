# file_operations/file_utils.py
import os

from rename_rules.rule_manager import analysis_rules

"""
文件操作模块
"""


def get_files_in_directory(directory):
    """获取指定目录的所有文件"""
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def rename_files(directory, old_name, new_name):
    """重命名文件"""
    os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))


def generate_new_name(rule, old_names):
    """
    功能：根据已加载的规则生成新文件名

    返回：新文件名列表
    """
    slip_char = rule['slip_char']
    zipped_names = analysis_rules(rule, old_names)
    new_names = []
    for i in range(len(zipped_names)):
        f, b, e = zipped_names[i]
        new = f + slip_char + b + e  # 新文件名为"front+slip_char+behind+ext"
        new_names.append(new)

    return new_names