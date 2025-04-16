# main.py
from log.log_recorder import *
from Fluent_Widgets_GUI.PyQt6_Fluent_GUI import *

"""
程序主模块
"""


def main():
    logging.info('程序启动')
    run_with_gui()
    logging.info('程序已退出')


if __name__ == '__main__':
    main()
