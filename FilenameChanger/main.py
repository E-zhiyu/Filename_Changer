# main.py
import time
from FilenameChanger.ui.cli import *
from FilenameChanger import version, author, config_path

"""
程序主模块
"""


def main():
    logger.info('程序启动')

    print_welcome(version, author)
    print_main_menu()

    logger.info('程序已退出')
    print('程序已退出……')
    time.sleep(0.5)


if __name__ == '__main__':
    main()
