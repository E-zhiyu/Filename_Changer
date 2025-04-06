# main.py
from FilenameChanger import version, author
from FilenameChanger.ui.cli import *


"""
程序主模块
"""


def main():
    logging.info('程序启动')

    print_welcome(version, author)
    print_main_menu()

    logging.info('程序已退出')
    print('感谢您的使用，期待与您再次相会！')
    time.sleep(0.5)


if __name__ == '__main__':
    main()
