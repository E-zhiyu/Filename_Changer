# ui/cli.py
import os

"""
此模块负责在命令行窗口与用户交互
"""


def get_directory():
    """
    功能：获取目标路径
    """
    while True:
        directory = input('请输入文件夹路径\n')

        # 去除前后双引号（如果有）
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

        # 路径有效性的异常处理
        try:
            if not os.path.isdir(directory):
                return directory
        except Exception as e:
            print(f'发生错误{e}，请重新输入！')
