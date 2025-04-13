# main.py
from FilenameChanger.cli.cli import *
from Fluent_Widgets_GUI.PyQt6_Fluent_GUI import *

"""
程序主模块
"""


def main():
    logging.info('程序启动')

    run_with_gui()
    # 已废弃的命令行界面
    """print_welcome(version, author)
    print_main_menu()"""

    logging.info('程序已退出')
    print('感谢您的使用，期待与您再次相会！')
    # time.sleep(0.5)


if __name__ == '__main__':
    main()
