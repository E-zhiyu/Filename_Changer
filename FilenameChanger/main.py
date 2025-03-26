# main.py
from FilenameChanger.ui.cli import *
from FilenameChanger.file_operations.file_utils import *
from FilenameChanger.rename_rules.rule_kind_inputer import *
import time

"""
程序主模块
"""
version = "1.0.0"
author = 'GitHub@E-zhiyu'

config_path = './rename_rules/rename_rules.json'  # 重命名规则文件路径


def main():
    print_welcome(version, author)
    while True:
        print('操作选择'.center(42, '—'))
        all_options="""
【0】结束该程序
【1】文件重命名
【2】写入规则
"""
        print(all_options)
        option = int(input('请选择：'))
        if option == 0:
            break
        elif option == 1:
            Rename()
        elif option == 2:
            input_new_rule(config_path)  # 输入新规则
        else:
            print('请选择有效的操作')

    print('程序已退出……')
    time.sleep(0.5)


# 功能：文件重命名
def Rename():
    rule = load_config(config_path)  # 加载已保存的规则
    if not rule:  # 若规则为空，则结束本函数
        print('规则为空，请先写入规则！')
        return

    directory = get_directory()  # 获取目标路径

    old_names = get_files_in_directory(directory)  # old_file_names列表将包含该目录下所有文件的文件名（包含扩展名）
    new_names = generate_new_name(rule, old_names)  # 生成新文件名

    if confirm_to_rename():  # 用户确认重命名后再执行
        for old, new in zip(old_names, new_names):
            rename_files(directory, old, new)  # 执行重命名操作


if __name__ == '__main__':
    main()
