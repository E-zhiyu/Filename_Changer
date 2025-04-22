# FilenameChanger/rename_rules/rule_type_manager.py
import re

from FilenameChanger.rename_rules.rule_manager import *

"""
根据规则种类采用不同写入和读取方式的模块
"""


def use_type_1(config_dict, old_name_list):
    """
    功能：应用类型一的规则
    参数 config_dict：配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    selected_index = config_dict['selected_index']
    split_char = config_dict['rules'][selected_index]['split_char']
    old_filename_list = []  # 文件名列表
    old_ext_list = []  # 扩展名列表
    for file in old_name_list:
        try:
            signal_name, signal_ext = os.path.splitext(file)  # 分离文件名和扩展名
        except ValueError:
            signal_ext = ''  # 处理没有扩展名的文件

        old_filename_list.append(signal_name)
        old_ext_list.append(signal_ext)

    front = []  # 前半部分文件名
    behind = []  # 后半部分文件名
    for signal_name in old_filename_list:
        parts = signal_name.split(split_char, maxsplit=1)  # 将拆分的两个部分存放至列表parts中
        f = parts[0]
        b = parts[1] if len(parts) > 1 else ''  # 默认第二部分为空，用于处理无法拆分的文件名
        front.append(f)
        behind.append(b)
    new_name_list = []
    for f, b, e in zip(front, behind, old_ext_list):
        f = f.strip()  # 去除前后空格
        if b:
            b = b.strip()  # 去除前后空格
            new = f'{b} {split_char} {f}{e}'  # 将f,b前后调换生成新文件名
        else:
            new = f'{f}{e}'  # 若没有第二部分文件名则保持原状
        new_name_list.append(new)  # 将新名字并入新文件名列表

    return new_name_list


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
        new_name = f'{signal_name}.{new_ext}'
        new_name_list.append(new_name)

    return new_name_list


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
        try:
            name, ext = os.path.splitext(file)
        except ValueError:
            ext = ''  # 处理没有扩展名的文件
        old_file_name_list.append(name)
        old_file_ext_list.append(ext)

    new_name_list = []
    for file_name, ext in zip(old_file_name_list, old_file_ext_list):
        try:
            f, b = file_name.split(target_str, 2)
            new_name = f'{f}{new_str}{b}{ext}'
        except ValueError:  # 处理无法拆分的情况
            new_name = f'{file_name}{ext}'
        new_name_list.append(new_name)

    return new_name_list


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

    try:
        y, m, d = config_dict['rules'][selected_index]['date'].split(' ')
        customize_date = f'{y}{split_char}{m}{split_char}{d}'
    except ValueError:  # 处理自定义日期为空的情况
        customize_date = ''

    new_name_list = []

    """遍历文件名列表，循环对单个文件名进行操作"""
    for old_name in old_name_list:
        try:
            file_name, ext = os.path.splitext(old_name)
        except ValueError:
            ext = ''  # 处理没有扩展名的文件（不用处理没有文件名的文件，因为这种文件不会被扫描进列表）

        """判断是否含有日期"""
        logging.info('判断文件名是否含有日期')
        date_type_re = (
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{8}',
            r'\d{4}_\d{1,2}_\d{1,2}',
            r'\d{4} \d{1,2} \d{1,2}',
            r'\d{4}年\d{1,2}月\d{1,2}日'
        )
        for date in date_type_re:
            if re.match(date, file_name):
                date_type = date  # 保存匹配到的日期样式
                logging.info(f'文件名含有日期，格式为“{date_type}”')
                with_date = True
                break
        else:
            logging.info('文件名不含日期')
            with_date = False

        if with_date:
            """删除日期操作"""
            new_name = re.sub(date_type, '', file_name) + ext
            logging.info('已删除文件名中的日期')
            new_name_list.append(new_name)
        else:
            """添加日期操作"""
            if customize_date:  # 判断自定义日期是否为空
                if position == 'head':
                    new_name = f'{customize_date}{file_name}{ext}'
                    logging.info(f'已将日期：“{customize_date}”添加至文件名头部')
                elif position == 'tail':
                    new_name = f'{file_name}{customize_date}{ext}'
                    logging.info(f'已将日期：“{customize_date}”添加至文件名尾部')
                new_name_list.append(new_name)
            else:
                if position == 'head':
                    new_name = f'{local_date}{file_name}{ext}'
                    logging.info('已将当前系统日期添加至文件名头部')
                elif position == 'tail':
                    new_name = f'{file_name}{local_date}{ext}'
                    logging.info('已将当前系统日期添加至文件名尾部')
                new_name_list.append(new_name)

    return new_name_list
