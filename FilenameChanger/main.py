# main.py
from ui.cli import *
from file_operations.file_utils import *
from config.config_manager import *
from rename_rules import *

"""
程序主模块
"""
version = "1.0.0"
author = 'E_zhiyu'

config_path = 'config/config.json'  # 默认配置文件路径


def main():
    print('【1】文件重命名 【2】自定义规则预设')
    option = int(input('请选择操作：'))
    if option == 1:
        Rename()
    elif option == 2:
        Set_rules()


# 自定义规则函数
def Set_rules():
    print('【1】交换特定符号前后的字符')


# 文件重命名函数
def Rename():
    directory = get_directory()
    old_file_names = get_files_in_directory(directory)  # old_file_names列表将包含该目录下所有文件的文件名
    rule = load_config(config_path)  # 加载已保存的规则
    new_name = generate_new_name(rule)  # 生成新文件名
    rename_files(directory, old_file_names, new_name)  # 执行重命名操作


if __name__ == '__main__':
    main()
