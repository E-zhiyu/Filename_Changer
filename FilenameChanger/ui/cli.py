# ui/cli.py
from FilenameChanger.file_operations.file_utils import *
from FilenameChanger.rename_rules.rule_kind_inputer import *
from FilenameChanger import config_path

"""
此模块负责在命令行窗口与用户交互
"""


def print_welcome(version, author):
    """
    功能：打印程序打开时的提示语
    参数 version：程序版本
    参数 author：作者昵称
    """
    title = '文件名管理器'
    welcom_mes = f"""
  版本：{version}
  作者：{author}
  欢迎使用本程序！本程序能够帮助您更加便捷地管理文件名。
    """
    print(title.center(42, '—'))
    print(welcom_mes)


def confirm_to_rename():
    """
    功能：提示操作的风险并确认用户操作
    返回：是否进行下一步操作（布尔值）
    """
    warning = """
  【警告】文件重命名可能伴随以下风险
  1.某些应用程序由于路径依赖无法定位重命名后的文件
  2.批量重命名可能影响该文件夹内的隐藏文件和受保护的文件
  3.受限于程序的功能，目前重命名操作不可逆！
    """
    print(warning)
    print('\n确认要重命名吗？（Y/N）')
    while True:
        option = input('请输入：')
        if option == 'Y' or option == 'y':
            logger.info('用户确认操作')
            return True
        elif option == 'N':
            logger.info('用户取消操作')
            return False
        else:
            print('请输入Y或者N！')


def get_directory():
    """
    功能：提示用户输入目标路径
    """
    while True:
        directory = input('请输入文件夹路径\n')

        # 去除前后双引号（如果有）
        if directory[0] == '\"':
            directory = directory[1:]
        if directory[-1] == '\"':
            directory = directory[:-1]
        directory = r''.join(list(directory))
        logger.info(f'输入路径“{directory}”')

        # 路径有效性的异常处理
        try:
            if os.path.isdir(directory):
                logger.info('路径有效，进行下一步操作')
                return directory
            else:
                print(f'“{directory}”不是有效的路径，请重新输入！')
                logger.info('路径无效，已提示用户重新输入')
        except Exception as e:
            print(f'发生错误{e}，请重新输入！')


def print_main_menu():
    all_options = """
【0】结束该程序
【1】文件重命名
【2】规则设置
        """
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
            rename(config_path)
        elif option == 2:
            print('操作：规则配置'.center(42, '—'))
            logger.info('选择操作：规则设置')
            configure_rules(config_path)
        else:
            print('请选择有效的操作')


def rename(config_path):
    """
    功能：实现“文件重命名”操作
    """
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
    print('操作已记录在日志文件中！')


def configure_rules(config_path):
    """
    功能：实现“规则设置”操作
    """
    usable_options = """
【0】回到上一步
【1】写入新规则
【2】查看规则
【3】删除规则
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

    if user_option == 0:
        logger.info('选择操作：回到上一步')
        return
    elif user_option == 1:
        logger.info('选择操作：写入新规则')
        set_new_rule(config_path)
    elif user_option == 2:
        logger.info('选择操作：查看规则')
        display_rules(config_path)
    elif user_option == 3:
        logger.info('选择操作：删除规则')
        del_rules(config_path)
