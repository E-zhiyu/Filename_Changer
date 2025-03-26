# file_operations/file_utils.py
from os import stat
import platform

from FilenameChanger.rename_rules.rule_manager import *

"""
文件操作模块
"""


def is_hidden_or_is_protected(directory):
    """
    功能：获取目标路径下的所有隐藏文件（支持Windows隐藏属性）和受保护（系统文件和只读文件）的文件名
    :param directory: 目标路径
    :return: 是否为需要排除的文件文件（布尔值）
    """
    name = os.path.basename(directory)
    if name.startswith('.'):
        return True

    if platform.system() == 'Windows':
        try:
            # 获取 Windows 文件属性标志位
            attrs = os.stat(directory).st_file_attributes
            # 检查是否隐藏（0x2）或系统文件（0x4）
            if attrs & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM):
                return True
            # 可选：排除只读文件（0x1）
            if attrs & stat.FILE_ATTRIBUTE_READONLY:
                return True
        except (AttributeError, OSError):
            pass  # 非 Windows 或文件不可访问
    return False


def get_files_in_directory(directory):
    """
    :param directory: 目标路径
    :return: 旧文件名列表
    """
    try:
        old_name = [f for f in os.listdir(directory) if
                    os.path.isfile(os.path.join(directory, f)) and not is_hidden_or_is_protected(
                        os.path.join(directory, f))]
        if not old_name:
            raise FileNotFoundError
    except FileNotFoundError:
        print(f'【错误】“{directory}”为空！')
    else:
        return old_name


def rename_files(directory, old_name, new_name):
    """
    功能：执行重命名操作并显示重命名结果
    :param directory:目标文件夹
    :param old_name:旧文件名
    :param new_name:新文件名
    """
    if old_name == new_name:
        print(f'【无法拆分】{old_name}')
    else:
        try:
            os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
        except FileNotFoundError:
            print(f'【错误】文件“{old_name}”不存在！')
        else:
            print(f'【成功】{old_name} -> {new_name}')


def generate_new_name(rule, old_names):
    """
    功能：根据已加载的规则生成新文件名
    返回：新文件名列表
    """
    split_char = rule['split_char']
    zipped_names = analysis_rules(rule, old_names)
    new_names = []
    for i in zipped_names:
        f, b, e = i  # 解包压缩的文件名
        # 去除前后空格

        if f[0] == ' ':
            f = f[1:]
        if f[-1] == ' ':
            f = f[:-1]
        if b:
            if b[0] == ' ':
                b = b[1:]
            if b[-1] == ' ':
                b = b[:-1]
            new = b + ' ' + split_char + ' ' + f + e  # 将f,b前后调换生成新文件名
        else:
            new = f + e  # 若没有第二部分文件名则保持原状
        new_names.append(new)  # 将新名字并入新文件名列表

    return new_names
