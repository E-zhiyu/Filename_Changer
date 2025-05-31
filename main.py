# main.py
from FilenameChanger.log.log_recorder import *
from FilenameChanger.Fluent_Widgets_GUI.PyQt6_Fluent_GUI import run_with_gui

"""
程序主模块
"""


def main():
    logging.info('程序启动')
    run_with_gui()


if __name__ == '__main__':
    main()
