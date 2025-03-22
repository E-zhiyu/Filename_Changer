# main.py
from ui.cli import *
from file_operations.file_utils import *
from config.config_manager import *

"""
程序主模块
"""


def main():
    directory = get_directory()
    old_file_names = get_files_in_directory(directory)  # old_file_names列表将包含该目录下所有文件的文件名
    rule = load_config()  # 加载已保存的规则


if __name__ == '__main__':
    main()
