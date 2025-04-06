# FilenameChanger/rename_rules/rule_type_manager.py
import re

from FilenameChanger.rename_rules.rule_manager import *
from FilenameChanger.rename_rules import illegal_char

"""
根据规则种类采用不同写入和读取方式的模块
"""


def set_new_rule(config_dict):
    """
    功能：提示用户输入规则
    参数 config_dict：配置文件根字典
    """
    all_rule_types = """
【1】交换特定符号前后内容
【2】批量修改文件扩展名
【3】更改文件名中特定字符串（每个文件仅修改一处）
【4】文件名增加或删除当前日期（开发中……）
    """
    print('创建新规则'.center(42, '—'))
    print('以下为所有规则类型')
    print(all_rule_types)

    cycle = True
    while cycle:
        try:
            rule_type = int(input('请选择（输入-1取消）：'))
            cycle = False  # 用户输入后更改循环条件跳出循环
            if rule_type == -1:
                logging.info('用户取消写入规则')
                print('已取消，正在返回主菜单……')
                time.sleep(0.5)
                return
        except ValueError:  # 防止没有输入
            print('请选择一个规则类型！')

    logging.info(f'用户选择规则类型{rule_type}')
    if rule_type == 1:
        input_type_1(config_dict)
    elif rule_type == 2:
        input_type_2(config_dict)
    elif rule_type == 3:
        input_type_3(config_dict)
    elif rule_type == 4:
        input_type_4(config_dict)
    else:
        print('【选择错误】你选择了一个不存在的操作！即将返回主菜单……')

    time.sleep(0.5)


def input_type_1(config_dict):
    """
    功能：输入规则类型一并保存
    规则类型：拆分特定分隔符前后的文件名并交换
    参数 config_dict：配置文件根字典
    """
    new_rule_dict = {}  # 创建文件名分割规则字典
    new_rule_dict['type'] = 1

    new_rule_dict['name'] = input('请输入规则名称：')
    logging.info(f'输入规则名称：“{new_rule_dict["name"]}”')
    new_rule_dict['desc'] = input('请输入规则描述：')
    logging.info(f'输入规则描述：“{new_rule_dict["desc"]}”')

    do_cycle = True
    while do_cycle:
        new_rule_dict['split_char'] = input('请输入分隔符：')
        if new_rule_dict['split_char'] in illegal_char:
            print(f'文件名不能包含{illegal_char}！')
        else:
            do_cycle = False
    logging.info(f'输入分隔符：“{new_rule_dict["split_char"]}”')

    save_new_rule(config_dict, new_rule_dict)  # 保存输入的规则


def use_type_1(config_dict, old_name_list):
    """
    功能：应用类型一的规则
    参数 config_dict：配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    selected_index = config_dict['selected_index']
    split_char = config_dict['rules'][selected_index]['split_char']
    name_list = []  # 文件名列表
    ext_list = []  # 扩展名列表
    for file in old_name_list:
        try:  # 处理没有扩展名的文件
            signal_name, signal_ext = os.path.splitext(file)  # 分离文件名和扩展名
        except ValueError:
            signal_ext = ''

        name_list.append(signal_name)
        ext_list.append(signal_ext)

    front = []  # 前半部分文件名
    behind = []  # 后半部分文件名
    for signal_name in name_list:
        parts = signal_name.split(split_char, maxsplit=1)  # 将拆分的两个部分存放至列表parts中
        f = parts[0]
        b = parts[1] if len(parts) > 1 else ''  # 默认第二部分为空，用于处理无法拆分的文件名
        front.append(f)
        behind.append(b)
    new_name_list = []
    for f, b, e in zip(front, behind, ext_list):
        f.strip()  # 去除前后空格
        if b:
            b.strip()  # 去除前后空格
            new = b + ' ' + split_char + ' ' + f + e  # 将f,b前后调换生成新文件名
        else:
            new = f + e  # 若没有第二部分文件名则保持原状
        new_name_list.append(new)  # 将新名字并入新文件名列表

    return new_name_list


def input_type_2(config_dict):
    """
    功能：输入规则类型二并保存
    规则类型：批量更改扩展名
    参数 config_dict：配置文件根字典
    """
    new_rule_dict = {}
    new_rule_dict['type'] = 2

    new_rule_dict['name'] = input('请输入规则名称：')
    logging.info(f'输入规则名称：“{new_rule_dict["name"]}”')
    new_rule_dict['desc'] = input('请输入规则描述：')
    logging.info(f'输入规则描述：“{new_rule_dict["desc"]}”')

    do_cycle = True
    while do_cycle:
        new_rule_dict['new_ext'] = input('请输入新的文件扩展名：')
        if new_rule_dict['new_ext'].startswith('.'):
            new_rule_dict['new_ext'] = new_rule_dict['new_ext'][1:]  # 去除用户输入的“.”
        """检测是否含有非法字符"""
        for char in illegal_char:
            if char in new_rule_dict['new_ext']:
                print(f'文件名不能包含{illegal_char}')
                break
        else:  # 循环正常结束则跳出while循环
            do_cycle = False
    logging.info(f'输入新文件扩展名：“{new_rule_dict["new_ext"]}”')

    save_new_rule(config_dict, new_rule_dict)


def use_type_2(config_dict, old_name_list):
    """
    功能：应用类型二的规则
    参数 config_dict：配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    selected_index = config_dict['selected_index']
    new_ext = config_dict['rules'][selected_index]['new_ext']

    name_list = []  # 文件名（排除扩展名）列表
    for file in old_name_list:
        signal_name = os.path.splitext(file)[0]  # 此规则不需要获取原来的扩展名
        name_list.append(signal_name)

    new_name_list = []
    for signal_name in name_list:
        new_name = signal_name + '.' + new_ext
        new_name_list.append(new_name)

    return new_name_list


def input_type_3(config_dict):
    """
    功能：输入规则类型三并保存
    规则类型：修改特定字符串
    参数 config_dict：配置文件根字典
    """
    new_rule_dict = {}
    new_rule_dict['type'] = 3

    new_rule_dict['name'] = input('请输入规则名称：')
    logging.info(f'输入规则名称：“{new_rule_dict["name"]}”')
    new_rule_dict['desc'] = input('请输入规则描述：')
    logging.info(f'输入规则描述：“{new_rule_dict["desc"]}”')

    do_cycle = True
    while do_cycle:
        new_rule_dict['target_str'] = input('请输入需要修改的字符串：')
        for char in illegal_char:
            if char in new_rule_dict['target_str']:
                print(f'文件名不能含有{illegal_char}！')
                break
        else:
            do_cycle = False
    logging.info(f'输入目标字符串：“{new_rule_dict["target_str"]}”')

    do_cycle = True
    while do_cycle:
        new_rule_dict['new_str'] = input('请输入修改后的字符串：')
        for char in illegal_char:
            if char in new_rule_dict['new_str']:
                print(f'文件名不能含有{illegal_char}！')
                break
        else:
            do_cycle = False
    logging.info(f'输入新字符串：“{new_rule_dict["new_str"]}”')

    save_new_rule(config_dict, new_rule_dict)


def use_type_3(config_dict, old_name_list):
    """
    功能：应用类型三的规则
    参数 config_dict：配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    selected_index = config_dict['selected_index']
    target_str = config_dict['rules'][selected_index]['target_str']  # 待替换的字符串
    new_str = config_dict['rules'][selected_index]['new_str']  # 新字符串

    old_file_name_list = []  # 文件名（排除扩展名）列表
    old_file_ext_list = []  # 文件扩展名列表
    for file in old_name_list:
        name, ext = os.path.splitext(file)
        old_file_name_list.append(name)
        old_file_ext_list.append(ext)

    new_name_list = []
    for file_name, ext in zip(old_file_name_list, old_file_ext_list):
        try:
            f, b = file_name.split(target_str, 2)
            new_name = f + new_str + b + ext
        except ValueError:  # 处理无法拆分的情况
            new_name = file_name + ext
        new_name_list.append(new_name)

    return new_name_list


def input_type_4(config_dict):
    """
    功能：输入规则类型四并保存
    规则类型：增加或移除文件名中的日期
    参数 config_dict：配置文件根字典
    """
    new_rule_dict = {}
    new_rule_dict['type'] = 4

    new_rule_dict['name'] = input('请输入规则名称：')
    logging.info(f'输入规则名称：“{new_rule_dict["name"]}”')
    new_rule_dict['desc'] = input('请输入规则描述：')
    logging.info(f'输入规则描述：“{new_rule_dict["desc"]}”')

    position = ''
    prompt = """
【1】文件名头部
【2】文件名尾部
    """
    print('请选择日期在文件名中的位置：')
    print(prompt)
    while position == '':
        try:
            user_option = int(input())
            if user_option == 1:
                position = 'head'
            elif user_option == 2:
                position = 'tail'
            else:
                print('请选择一个有效值！')
        except ValueError:
            print('该选项为必填选项，请不要跳过输入！')
    logging.info(f'输入日期在文件名中的位置：“{position}”')
    new_rule_dict['position'] = position

    do_cycle = True
    while do_cycle:
        new_rule_dict['split_char'] = input('请输入年月日分隔符：')
        if new_rule_dict['split_char'] in illegal_char:  # 检测输入的分隔符是否合法
            print(f'文件名不能包含{illegal_char}！')
        else:
            do_cycle = False
    logging.info(f'输入年月日分隔符：“{new_rule_dict["split_char"]}”')

    save_new_rule(config_dict, new_rule_dict)


def use_type_4(config_dict, old_name_list):
    """
    功能：应用类型四的规则
    参数 config_dict：配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    selected_index = config_dict['selected_index']
    split_char = config_dict['rules'][selected_index]['split_char']
    position = config_dict['rules'][selected_index]['position']
    local_date = time.strftime(f'%Y{split_char}%m{split_char}%d', time.localtime(time.time()))
    new_name_list = []

    """遍历文件名列表，循环对单个文件名进行操作"""
    for old_name in old_name_list:
        try:  # 处理没有扩展名的文件
            file_name, ext = os.path.splitext(old_name)
        except ValueError:
            ext = ''

        """判断是否含有日期"""
        date_type_re = (
            '\d{4}-\d{1,2}-\d{1,2}',
            '\d{8}',
            '\d{4}_\d{1,2}_\d{1,2}',
            '\d{4} \d{1,2} \d{1,2}',
            '\d{4}年\d{1,2}月\d{1,2}日'
        )
        for date in date_type_re:
            if re.match(date, file_name):
                date_type = date  # 保存匹配到的日期样式
                with_date = True
                break
        else:
            with_date = False

        if with_date:
            """删除日期操作"""
            new_name = re.sub(date_type, '', file_name) + ext
            new_name_list.append(new_name)
        else:
            """添加日期操作"""
            if position == 'head':
                new_name = local_date + file_name + ext
            elif position == 'tail':
                new_name = file_name + local_date + ext
            new_name_list.append(new_name)

    return new_name_list
