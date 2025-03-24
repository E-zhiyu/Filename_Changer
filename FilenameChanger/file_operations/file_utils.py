# file_operations/file_utils.py
from FilenameChanger.rename_rules.rule_manager import *

"""
文件操作模块
"""


def get_files_in_directory(directory):
    """
    :param directory: 目标路径
    :return: 旧文件名列表
    """
    try:
        old_name = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        if old_name == []:
            raise FileNotFoundError
    except FileNotFoundError as e:
        print(f'【文件未找到】{e}：该文件夹为空！')
    else:
        return old_name


def rename_files(directory, old_name, new_name):
    """
    功能：执行重命名操作并显示重命名结果
    :param directory:目标文件夹
    :param old_name:旧文件名
    :param new_name:新文件名
    """
    try:
        os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
    except FileNotFoundError as e:
        print(f'【文件存在性异常】\n文件：{old_name}不存在！')
    else:
        print(f'成功：{old_name} -> {new_name}')


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
        if f != '':
            if f[0] == ' ':
                f = f[1:]
            if f[-1] == ' ':
                f = f[:-1]
        if b != '':
            if b[0] == ' ':
                b = b[1:]
            if b[-1] == ' ':
                b = b[:-1]
            new = b + ' ' + split_char + ' ' + f + e  # 将f,b前后调换生成新文件名
        else:
            new = f + e  # 若没有第二部分文件名则保持原状
        new_names.append(new)  # 将新名字并入新文件名列表

    return new_names
