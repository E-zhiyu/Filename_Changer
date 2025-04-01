# file_operations/file_utils.py
import platform  # 判断系统类型
import stat  # 判断文件属性

from FilenameChanger.rename_rules.rule_manager import *
from FilenameChanger.rename_rules.rule_type_manager import *

"""
功能：实现对文件的操作
"""


def is_hidden_or_is_protected(directory):
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
                    os.path.isfile(os.path.join(directory, f)) and not is_hidden_or_is_protected(
                        os.path.join(directory, f))]
        logger.info('文件名列表获取成功')
        if not old_name:
            raise FileNotFoundError
    except FileNotFoundError:
        logger.error('目标路径为空，文件名列表获取失败')
        print(f'【错误】“{directory}”为空！')
    else:
        return old_name


def rename_files(directory, old_name, new_name):
    """
    功能：为单个文件重命名并显示结果
    参数 directory：目标文件夹
    参数 old_name：单个旧文件名
    参数 new_name：单个新文件名
    """
    if old_name == new_name:
        logger.info(f'【未更改】{old_name}')
        print(f'【未更改】{old_name}')
    else:
        try:
            os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
        except FileNotFoundError:
            logger.error(f'【错误】文件“{old_name}”不存在！')
            print(f'【错误】文件“{old_name}”不存在！')
        else:
            logger.info(f'【成功】{old_name} -> {new_name}')
            print(f'【成功】{old_name} -> {new_name}')


def get_new_name_list(config_dict, old_name_list):
    """
    功能：根据已加载的规则生成新文件名
    参数 config_dict：规则配置文件根字典
    参数 old_name_list：旧文件名列表
    返回：新文件名列表
    """
    selected=config_dict['selected_index']

    if config_dict['rules'][selected]['type'] == 1:
        new_name_list = use_type_1(config_dict, old_name_list)
    if config_dict['rules'][selected]['type'] == 2:
        new_name_list = use_type_2(config_dict, old_name_list)

    logger.info('已生成新文件名列表')
    return new_name_list
