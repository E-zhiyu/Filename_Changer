# FilenameChanger/rename_rules/rule_type_manager.py
import re
import time

from FilenameChanger.rename_rules.rule_manager import *

"""
根据规则种类采用不同写入和读取方式的模块
"""


def use_type_1(selected_rule, old_name_list):
    """
    功能：应用类型一的规则（交换分隔符前后内容）
    参数 selected_rule：当前激活的规则
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    split_char = selected_rule['split_char']
    old_filename_list = []  # 文件名列表
    old_ext_list = []  # 扩展名列表
    for file in old_name_list:
        signal_name, signal_ext = os.path.splitext(file)  # 分离文件名和扩展名

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


def use_type_2(selected_rule, old_name_list):
    """
    功能：应用类型二的规则（扩展名替换）
    参数 selected_rule：当前激活的规则
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    new_ext = selected_rule['new_ext']

    name_list = []  # 文件名（排除扩展名）列表
    for file in old_name_list:
        signal_name = os.path.splitext(file)[0]
        name_list.append(signal_name)

    new_name_list = []
    for signal_name in name_list:
        new_name = f'{signal_name}.{new_ext}'
        new_name_list.append(new_name)

    return new_name_list


def use_type_3(selected_rule, old_name_list):
    """
    功能：应用类型三的规则（字符串替换）
    参数 当前激活的规则：配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    target_str = selected_rule['target_str']  # 待替换的字符串
    new_str = selected_rule['new_str']  # 新字符串
    use_re = selected_rule.get('use_re', False)  # 判断是否使用正则表达式

    # 分离文件名和扩展名
    old_file_name_list = []  # 文件名（排除扩展名）列表
    old_file_ext_list = []  # 文件扩展名列表
    for file in old_name_list:
        name, ext = os.path.splitext(file)

        old_file_name_list.append(name)
        old_file_ext_list.append(ext)

    new_name_list = []
    for file_name, ext in zip(old_file_name_list, old_file_ext_list):
        if use_re:
            new_name = f'{re.sub(target_str, new_str, file_name)}{ext}'
        else:
            new_name = f'{file_name.replace(target_str, new_str)}{ext}'

        new_name_list.append(new_name)

    return new_name_list


def get_file_time(file_path, time_type, split_char):
    """
    功能：获取文件日期
    参数 file_path：文件路径
    参数 time_type：需要返回的时间类型
    返回：创建时间、修改时间和访问时间三者之一
    """
    if time_type == 0:
        logging.info('待填充的日期：系统日期')
        date = time.time()
    elif time_type == 1:
        logging.info('待填充的日期：文件创建日期')
        date = os.path.getctime(file_path)
    elif time_type == 2:
        logging.info('待填充的日期：文件修改日期')
        date = os.path.getmtime(file_path)
    elif time_type == 3:
        logging.info('待填充的日期：文件访问日期')
        date = os.path.getatime(file_path)

    if split_char == '年月日':
        format_date = time.strftime('%Y年%m月%d日', time.localtime(date))
    else:
        format_date = time.strftime(f'%Y{split_char}%m{split_char}%d', time.localtime(date))

    return format_date


def use_type_4(selected_rule, old_name_list, directory):
    """
    功能：应用类型四的规则（添加或删除日期）
    参数 selected_rule：当前激活的规则
    参数 old_name_list：旧文件名列表
    参数 directory：目标文件夹路径
    返回：生成的新文件名列表
    """
    split_char = selected_rule['split_char'] if selected_rule['split_char'] != '空格' else ' '
    position = selected_rule['position']

    try:
        y, m, d = selected_rule['date'].split(' ')
        if split_char == '年月日':
            customize_date = f'{y}年{m}月{d}日'
        else:
            customize_date = f'{y}{split_char}{m}{split_char}{d}'
    except (KeyError, AttributeError, ValueError):  # 处理自定义日期为空的情况
        customize_date = ''

    time_type = selected_rule.get('date_type', 4 if customize_date else 0)  # 处理v2.1.0及更旧版本的规则

    new_name_list = []

    """遍历文件名列表，循环对单个文件名进行操作"""
    for old_name in old_name_list:
        # 获取文件日期
        if time_type != 4:
            file_date = get_file_time(os.path.join(directory, old_name), time_type, split_char)
            logging.info(f'已获取日期：“{file_date}”')
        else:
            logging.info('待填充的日期：自定义日期')
            file_date = customize_date

        file_name, ext = os.path.splitext(old_name)  # 分离文件名和扩展名
        date_re = r'[-_ ]?\d{4}[-_ 年]?\d{1,2}[-_ 月]?\d{1,2}[-_ 日]?'  # 日期匹配的模式串

        """删除文件名中的日期"""
        date_removed_name = re.sub(date_re, '', file_name)
        if re.findall(date_re, file_name):
            logging.info('文件名含有日期，已将其删除')
        else:
            logging.info('文件名不含日期')

        """添加指定日期"""
        if time_type == 4:  # 判断该规则是否填充自定义日期
            if position == 'head':
                new_name = f'{customize_date}{split_char}{date_removed_name}{ext}' if split_char != '年月日' \
                    else f'{customize_date}-{date_removed_name}{ext}'
                if customize_date:
                    logging.info(f'已将日期：“{customize_date}”添加至文件名头部')
            elif position == 'tail':
                new_name = f'{date_removed_name}{split_char}{customize_date}{ext}' if split_char != '年月日' \
                    else f'{date_removed_name}-{customize_date}{ext}'
                if customize_date:
                    logging.info(f'已将日期：“{customize_date}”添加至文件名尾部')
            new_name_list.append(new_name)
        else:
            if position == 'head':
                new_name = f'{file_date}{split_char}{date_removed_name}{ext}' if split_char != '年月日' \
                    else f'{file_date}-{date_removed_name}{ext}'
                logging.info(f'已将{file_date}添加至文件名头部')
            elif position == 'tail':
                new_name = f'{date_removed_name}{split_char}{file_date}{ext}' if split_char != '年月日' \
                    else f'{date_removed_name}-{file_date}{ext}'
                logging.info(f'已将{file_date}添加至文件名尾部')
            new_name_list.append(new_name)

    return new_name_list


def use_type_5(selected_rule, old_name_list):
    """
    功能：应用类型五的规则（重命名并编号）
    参数 当前激活的规则：配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：生成的新文件名列表
    """
    new_file_name = selected_rule['new_name']
    num_type = selected_rule['num_type']
    position = selected_rule['position']
    number = selected_rule['start_num']
    step_length = selected_rule['step_length']

    new_name_list = []

    for old_name in old_name_list:
        # 分离文件名和扩展名
        ext = os.path.splitext(old_name)[1]

        # 生成编号
        if position == 'head':
            if num_type == '1.':
                serial_number = f'{number}.'
            elif num_type == '1-':
                serial_number = f'{number}-'
            elif num_type == '1_':
                serial_number = f'{number}_'
        elif position == 'tail':
            if num_type == '1.':
                serial_number = f'.{number}'
            elif num_type == '1-':
                serial_number = f'-{number}'
            elif num_type == '1_':
                serial_number = f'_{number}'

        if num_type == '(1)':
            serial_number = f'({number})'
        elif num_type == '[1]':
            serial_number = f'[{number}]'
        elif num_type == '{1}':
            serial_number = '{' + str(number) + '}'

        # 将编号合并至文件名
        if position == 'head':
            new_name = f'{serial_number}{new_file_name}{ext}'
        elif position == 'tail':
            new_name = f'{new_file_name}{serial_number}{ext}'

        new_name_list.append(new_name)
        number += step_length

    return new_name_list
