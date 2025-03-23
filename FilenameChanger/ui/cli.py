# ui/cli.py
"""
此模块负责在命令行窗口与用户交互
"""
from os import remove


def get_directory():
    """
    功能：获取目标路
    """
    directory = input('请输入文件夹路径\n')

    # 去除前后双引号
    if directory[0] == '\"':
        directory = directory[1:]
    if directory[-1] == '\"':
        directory = directory[:-1]

    # 将斜杠替换为反斜杠
    list_directory = list(directory)
    for item in list_directory:
        if item == '\\':
            list_directory[list_directory.index(item)] = "/"
    directory = "".join(list_directory)

    return directory


def display_results():
    """显示重命名结果"""
    pass
