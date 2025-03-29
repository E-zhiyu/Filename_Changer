# main.py
from FilenameChanger.ui.cli import *
from FilenameChanger.file_operations.file_utils import *
from FilenameChanger.rename_rules.rule_kind_inputer import *
import time

from FilenameChanger.log.log_recorder import *

logger = logging.getLogger(__name__)

"""
程序主模块
"""
version = "1.0.0"
author = 'GitHub@E-zhiyu'
config_path = './rename_rules/rename_rules.json'  # 重命名规则文件路径


def main():
    logger.info('程序启动')
    all_options = """
【0】结束该程序
【1】文件重命名
【2】规则设置
    """
    print_welcome(version, author)
    while True:
        print('主菜单'.center(42, '—'))
        print(all_options)

        try:
            option = int(input('请选择：'))
        except ValueError:  # 防止没有输入内容
            print('请选择一个操作！')
            continue

        if option == 0:
            break
        elif option == 1:
            logger.info('选择操作：文件重命名')
            print('操作：文件重命名'.center(42, '—'))
            rename()
        elif option == 2:
            print('操作：规则配置'.center(42, '—'))
            logger.info('选择操作：规则设置')
            configure_rules()
        else:
            print('请选择有效的操作')

    logger.info('程序已退出')
    print('程序已退出……')
    time.sleep(0.5)


# 功能：文件重命名
def rename():
    all_rules = load_config(config_path)  # 加载已保存的规则
    if not all_rules['rules']:  # 若规则为空，则结束本函数
        print('规则为空，请先前往规则设置写入规则！')
        return

    directory = get_directory()  # 获取目标路径
    old_names = get_files_in_directory(directory)  # old_file_names列表将包含该目录下所有文件的文件名（包含扩展名）
    if not old_names:
        return
    new_names = generate_new_name(all_rules, old_names)  # 生成新文件名

    if confirm_to_rename():  # 用户确认重命名后再执行
        print('文件重命名记录'.center(42, '—'))
        for old, new in zip(old_names, new_names):
            rename_files(directory, old, new)  # 执行重命名操作
    print('文件重命名完成！')
    print('最新日志已存放至log文件夹！')


# 功能：进行规则设置
def configure_rules():
    usable_options = """
【0】回到上一步
【1】写入新规则
【2】查看规则
【3】删除规则
"""
    print(usable_options)
    cycle = True
    while cycle:
        try:
            option = int(input('请选择：'))
            cycle = False
        except ValueError:  # 防止没有输入操作
            print('请选择一个操作！')
            continue

    if option == 0:
        logger.info('选择操作：回到上一步')
        return
    elif option == 1:
        logger.info('选择操作：写入新规则')
        set_new_rule(config_path)
    elif option == 2:
        logger.info('选择操作：查看规则')
        display_rules(config_path)
    elif option == 3:
        logger.info('选择操作：删除规则')
        del_rules(config_path)


if __name__ == '__main__':
    main()
