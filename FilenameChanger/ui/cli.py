# ui/cli.py
import os
from FilenameChanger.log.log_recorder import *

"""
此模块负责在命令行窗口与用户交互
"""


def print_welcome(version, author):
    """
    功能：打印程序打开时的提示语
    """
    title = '文件名管理器'
    welcom_mes = f"""
  版本：{version}
  作者：{author}
  欢迎使用本程序！本程序能够帮助您更加便捷地管理文件名。
    """
    print(title.center(42, '—'))
    print(welcom_mes)


def confirm_to_rename():
    """
    功能：提示操作的风险并确认用户操作
    return:是否进行下一步操作（布尔值）
    """
    warning = """
  【警告】文件重命名可能伴随以下风险
  1.某些应用程序由于路径依赖无法定位重命名后的文件
  2.批量重命名可能影响该文件夹内的隐藏文件和受保护的文件
  3.受限于程序的功能，目前重命名操作不可逆！
    """
    print(warning)
    print('\n确认要重命名吗？（Y/N）')
    while True:
        option = input('请输入：')
        if option == 'Y' or option == 'y':
            logger.info('用户确认操作')
            return True
        elif option == 'N':
            logger.info('用户取消操作')
            return False
        else:
            print('请输入Y或者N！')


def get_directory():
    """
    功能：获取目标路径
    """
    while True:
        directory = input('请输入文件夹路径\n')
        logger.info(f'输入路径“{directory}”')

        # 去除前后双引号（如果有）
        if directory[0] == '\"':
            directory = directory[1:]
        if directory[-1] == '\"':
            directory = directory[:-1]
        directory = r''.join(list(directory))

        # 路径有效性的异常处理
        try:
            if os.path.isdir(directory):
                return directory
            else:
                print(f'“{directory}”不是有效的路径，请重新输入！')
        except Exception as e:
            print(f'发生错误{e}，请重新输入！')
