# main.py
from FilenameChanger.ui.cli import *
from FilenameChanger.file_operations.file_utils import *
from FilenameChanger.rename_rules.rule_manager import *
from FilenameChanger.rename_rules.rule_kind_inputer import *

"""
程序主模块
"""
version = "1.0.0"
author = 'E_zhiyu'

config_path = '../FilenameChanger/rename_rules/rename_rules.json'  # 默认重命名规则文件路径


def main():
    print('【1】文件重命名 【2】自定义规则预设')
    option = int(input('请选择操作：'))
    if option == 1:
        Rename()
    elif option == 2:
        Set_rules()


# 功能：自定义规则
def Set_rules():
    input_new_rule(config_path)


# 功能：文件重命名
def Rename():
    directory = get_directory()  # 获取目标路径
    old_names = get_files_in_directory(directory)  # old_file_names列表将包含该目录下所有文件的文件名（包含扩展名）
    rule = load_config(config_path)  # 加载已保存的规则
    new_names = generate_new_name(rule, old_names)  # 生成新文件名
    for old, new in zip(old_names, new_names):
        rename_files(directory, old, new)  # 执行重命名操作


if __name__ == '__main__':
    main()
