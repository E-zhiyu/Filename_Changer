# file_operations/file_utils.py
import platform  # 判断系统类型
import stat  # 判断文件属性

from FilenameChanger import history_file_path
from FilenameChanger.rename_rules.rule_type_manager import *

"""
功能：实现对文件的操作
"""


def hidden_or_protected(directory):
    """
    功能：获取目标路径下的所有隐藏文件（支持Windows隐藏属性）和受保护（系统文件和只读文件）的文件名
    参数 directory：目标路径
    返回：是否为需要排除的文件文件（布尔值）
    """
    name = os.path.basename(directory)
    if name.startswith('.'):  # 若文件名以'.'开头则直接判断为隐藏文件
        return True
    if platform.system() == 'Windows':
        try:
            # 获取 Windows 文件属性标志位
            attrs = os.stat(directory).st_file_attributes
            # 检查是否隐藏（0x2）或系统文件（0x4）
            if attrs & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM):
                logger.debug(f'排除隐藏文件或系统文件：“{directory}”')
                return True
            # 排除只读文件（0x1）
            if attrs & stat.FILE_ATTRIBUTE_READONLY:
                logger.debug(f'排除只读文件：{directory}')
                return True
        except (AttributeError, OSError):
            pass  # 非 Windows 或文件不可访问
    return False


def get_files_in_directory(directory):
    """
    功能：扫描目标路径的所有文件名
    参数 directory：目标路径
    返回：旧文件名列表
    """
    try:
        old_name = [f for f in os.listdir(directory) if
                    os.path.isfile(os.path.join(directory, f)) and not hidden_or_protected(
                        os.path.join(directory, f))]
        logger.info('文件名列表获取成功')
        if not old_name:
            raise FileNotFoundError
    except FileNotFoundError:
        logger.error('目标路径为空，文件名列表获取失败')
        print(f'【错误】“{directory}”为空！')
    else:
        return old_name


def rename_files(directory, origin_name, new_name):
    """
    功能：为单个文件重命名并显示结果
    参数 directory：目标文件夹
    参数 origin_name：单个原文件名
    参数 new_name：单个新文件名
    """
    if origin_name == new_name:
        logger.info(f'【未更改】{origin_name}')
        print(f'【未更改】{origin_name}')
    else:
        try:
            os.rename(os.path.join(directory, origin_name), os.path.join(directory, new_name))
        except FileNotFoundError:
            logger.error(f'【错误】文件“{origin_name}”不存在！')
            print(f'【错误】文件“{origin_name}”不存在！')
        else:
            logger.info(f'【成功】{origin_name} -> {new_name}')
            print(f'【成功】{origin_name} -> {new_name}')


def get_new_name_list(config_dict, old_name_list):
    """
    功能：根据已加载的规则生成新文件名
    参数 config_dict：规则配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：新文件名列表
    """
    selected = config_dict['selected_index']
    rule_type = config_dict['rules'][selected]['type']

    if rule_type == 1:
        new_name_list = use_type_1(config_dict, old_name_list)
    elif rule_type == 2:
        new_name_list = use_type_2(config_dict, old_name_list)
    elif rule_type == 3:
        new_name_list = use_type_3(config_dict, old_name_list)

    logger.info('已生成新文件名列表')
    return new_name_list


def cancel_last_operation():
    """
    功能：撤销上一次重命名操作
    """
    # 加载已保存的历史记录
    try:
        with open(history_file_path, 'r', encoding='utf-8') as f:
            logger.info('成功读取已保存的历史记录')
            history_dict = json.load(f)
    except FileNotFoundError:
        logger.error('历史记录文件不存在或被移除')
        print('历史记录文件不存在或已被移除！\n即将返回主菜单……')
        time.sleep(0.5)
        return

    # 判断历史记录是否为空
    if history_dict['max_index'] == -1:
        logger.error('历史记录为空，无法撤销重命名')
        print('历史记录为空！\n即将返回主菜单……')
        time.sleep(0.5)
        return

    # 加载上一次的重命名记录
    last_history_index = history_dict['max_index']
    last_history_dict = history_dict['history'][last_history_index]
    old_name_list = last_history_dict['old_name_list']  # 加载旧文件名列表
    new_name_list = last_history_dict['new_name_list']  # 加载新文件名列表
    directory = last_history_dict['directory']  # 加载目标文件夹路径

    # 判断旧文件夹路径是否可用
    if not os.path.isdir(directory):
        logger.error('无法撤销：旧文件夹路径无效')
        print('无法撤销：旧文件夹不存在或已被移除！\n即将返回主菜单……')
        time.sleep(0.5)
        return

    # 删除最近一条重命名记录
    del history_dict['history'][last_history_index]
    history_dict['max_index'] -= 1
    if not os.path.isdir(history_file_path):  # 防止历史记录文件夹被移除
        os.mkdir(os.path.dirname(history_file_path))
    with open(history_file_path, 'w', encoding='utf-8') as f:
        json.dump(history_dict, f, ensure_ascii=False, indent=4)

    # 撤销上一次重命名
    print('撤销上一次重命名'.center(42, '—'))
    for old, new in zip(old_name_list, new_name_list):
        rename_files(directory, new, old)


def record_history(old_name_list, new_name_list, directory):
    """
    功能：记录重命名历史记录
    参数 old_name_list：旧文件名列表
    参数 new_name_list：新文件名列表
    参数 directory：目标文件夹路径
    """
    # 创建历史记录文件夹
    if not os.path.isdir(os.path.dirname(history_file_path)):
        os.mkdir(os.path.dirname(history_file_path))

    # 读取现有历史记录
    try:
        with open(history_file_path, 'r', encoding='utf-8') as f:
            logger.info('成功读取已保存的历史记录')
            history_dict = json.load(f)
    except FileNotFoundError:
        with open(history_file_path, 'w', encoding='utf-8') as f:
            logger.info('历史记录文件不存在，正在初始化……')
            history_dict = {'max_index': -1, 'history': []}
            json.dump(history_dict, f, ensure_ascii=False, indent=4)
            logger.info('历史记录文件初始化成功')

    # 将新历史记录合并至根字典
    new_record_dict = {'directory': directory, 'old_name_list': old_name_list, 'new_name_list': new_name_list}
    history_dict['history'].append(new_record_dict)
    history_dict['max_index'] = len(history_dict['history']) - 1
    with open(history_file_path, 'w', encoding='utf-8') as f:
        json.dump(history_dict, f, ensure_ascii=False, indent=4)
        logger.info('已保存一条新的历史记录')
