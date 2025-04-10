# cli/cli.py

from FilenameChanger.file_operations.file_utils import *
from FilenameChanger.rename_rules.rule_type_manager import *

"""
此模块负责在命令行窗口与用户交互
"""


def print_welcome(version, author):
    """
    功能：打印程序启动时的提示语
    参数 version：程序版本
    参数 author：作者昵称
    """
    title = '文件更名器'
    welcom_mes = f"""
  版本：{version}
  作者：{author}
  欢迎使用本程序！本程序能够帮助您更加便捷地更改文件名。
    """
    print(title.center(42, '—'))
    print(welcom_mes)


def print_main_menu():
    all_options = """
【0】结束该程序
【1】文件重命名
【2】撤销上一次重命名操作
【3】规则设置
        """
    while True:
        print('主菜单'.center(42, '—'))
        print(all_options)

        try:
            option = int(input('请选择：'))
        except ValueError:  # 防止没有输入内容
            print('请选择一个操作！')
            time.sleep(0.5)
            continue

        if option == 0:
            break
        elif option == 1:
            logging.info('选择操作：文件重命名')
            print('操作：文件重命名'.center(42, '—'))
            rename()
        elif option == 2:
            logging.info('选择操作：撤销重命名')
            if confirm_your_operation(with_warning=False):
                cancel_last_operation()
        elif option == 3:
            print('操作：规则配置'.center(42, '—'))
            logging.info('选择操作：规则设置')
            configure_rules()
        else:
            print('请选择有效的操作')


def confirm_your_operation(with_warning=True):
    """
    功能：提示操作的风险并确认用户操作
    返回：是否进行下一步操作（布尔值）
    """
    warning = """
  【警告】文件重命名可能伴随以下风险
  1.某些应用程序由于路径依赖无法定位重命名后的文件。
  2.如果文件夹内有您不想重命名的文件，它也会被重命名！
    """
    if with_warning:
        print(warning)

    print('\n确认进行下一步操作吗？（Y/N）')
    while True:
        option = input('请输入：')
        if option == 'Y' or option == 'y':
            logging.info('用户确认操作')
            return True
        elif option == 'N' or option == 'n':
            logging.info('用户取消操作')
            return False
        else:
            print('请输入Y或者N！')


def get_directory():
    """
    功能：提示用户输入目标路径
    """
    while True:
        directory = input('请输入文件夹路径\n')
        if not directory:
            print('路径不能为空！')
            continue

        # 去除前后双引号
        directory = directory.strip('"')
        logging.info(f'输入路径“{directory}”')

        # 路径有效性的异常处理
        try:
            if os.path.isdir(directory):
                logging.info('路径有效，进行下一步操作')
                return directory
            else:
                print(f'“{directory}”不是有效的路径，请重新输入！')
                logging.info('路径无效，已提示用户重新输入')
        except Exception as e:
            print(f'发生错误{e}，请重新输入！')


def rename():
    """
    功能：实现“文件重命名”操作
    """
    config_dict = load_config()  # 加载已保存的规则
    logging.info(
        f'当前活跃的规则为“规则{config_dict['selected_index'] + 1}”，'
        f'规则种类：{config_dict['rules'][config_dict['selected_index']]['type']}')
    if not config_dict['rules']:  # 若规则为空，则结束本函数
        print('规则为空，请先前往规则设置写入规则！')
        return

    directory = get_directory()  # 获取目标路径

    if confirm_your_operation():  # 用户确认重命名后再执行
        old_name_list = get_files_in_directory(directory)  # old_file_names列表将包含该目录下所有文件的文件名（包含扩展名）
        if not old_name_list:
            return
        new_name_list = get_new_name_list(config_dict, old_name_list)  # 生成新文件名
        # 记录本次重命名操作，便于后续恢复
        if old_name_list != new_name_list:
            record_history(old_name_list, new_name_list, directory)

        print('文件重命名记录'.center(42, '—'))
        logging.info('开始文件重命名……')
        for old, new in zip(old_name_list, new_name_list):
            rename_files(directory, old, new)  # 执行重命名操作

    print('文件重命名完成！')
    print('操作已记录在日志文件中！')
    time.sleep(0.5)


def configure_rules():
    """
    功能：实现“规则设置”操作
    """
    usable_options = """
【0】回到主菜单
【1】创建新规则
【2】查看规则
【3】删除规则
【4】切换规则
"""
    print(usable_options)
    do_cycle = True  # 控制是否重新要求用户输入
    while do_cycle:
        try:
            user_option = int(input('请选择：'))
            do_cycle = False
        except ValueError:  # 防止没有输入操作
            print('请选择一个操作！')
            continue

    config_dict = load_config()
    logging.info(
        f'当前活跃的规则为“规则{config_dict['selected_index'] + 1}”，'
        f'规则种类：{config_dict['rules'][config_dict['selected_index']]['type']}')
    if user_option == 0:
        logging.info('选择操作：回到主菜单')
        return
    elif user_option == 1:
        logging.info('选择操作：创建新规则')
        set_new_rule(config_dict)
    elif user_option == 2:
        logging.info('选择操作：查看规则')
        display_rules(config_dict)
    elif user_option == 3:
        logging.info('选择操作：删除规则')
        del_rules(config_dict)
    elif user_option == 4:
        logging.info('选择操作：切换规则')
        switch_rule(config_dict)
