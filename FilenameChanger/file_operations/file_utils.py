# file_operations/file_utils.py
import platform  # 判断系统类型
import stat  # 判断文件属性

from FilenameChanger import history_file_path
from FilenameChanger.rename_rules.rule_type_manager import *
from FilenameChanger.history_operations.history_operations import load_history

"""
文件操作模块
"""


def is_directory_usable(directory):
    """
    功能：判断文件夹路径是否有效
    """
    if directory:
        # 去除前后双引号
        directory = directory.strip('"')
        logging.info(f'输入路径“{directory}”')

        # 路径有效性的异常处理
        try:
            if os.path.isdir(directory):
                logging.info('路径有效，进行下一步操作')
                return directory, 1
            else:
                logging.warning('路径无效')
                return directory, 0
        except Exception as e:
            logging.error('【错误】输入路径时发生未知错误！')
            return directory, 0
    else:
        logging.info('用户清空输入框的路径')
        return None, -1


def rename(directory):
    """
    功能：实现“文件重命名”操作
    """
    config_dict = load_config()  # 重命名时加载已保存的规则
    if not config_dict['rules']:  # 若规则为空，则结束本函数
        logging.info('规则为空，请先前往规则设置写入规则！')
        return -1
    logging.info(
        f'当前活跃的规则为“规则{config_dict['selected_index'] + 1}”，'
        f'规则种类：{config_dict['rules'][config_dict['selected_index']]['type']}')

    old_name_list = get_files_in_directory(directory)  # old_file_names列表将包含该目录下所有文件的文件名（包含扩展名）
    if not old_name_list:  # 判断文件夹是否为空，为空则返回0
        return 0
    new_name_list = get_new_name_list(config_dict, old_name_list)  # 生成新文件名

    logging.info('开始文件重命名……')
    rename_files(directory, old_name_list, new_name_list)  # 执行重命名操作

    return 1


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
                logging.debug(f'排除隐藏文件或系统文件：“{directory}”')
                return True
            # 排除只读文件（0x1）
            if attrs & stat.FILE_ATTRIBUTE_READONLY:
                logging.debug(f'排除只读文件：{directory}')
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
        logging.info('文件名列表获取成功')
        if not old_name:
            raise FileNotFoundError
    except FileNotFoundError:
        logging.error('目标路径为空，文件名列表获取失败')
        return None
    else:
        return old_name


def rename_files(directory, old_name_list, new_name_list, with_record_history=True):
    """
    功能：为单个文件重命名并显示结果
    参数 directory：目标文件夹
    参数 origin_name：单个原文件名
    参数 new_name：单个新文件名
    参数 with_record_history：是否记录重命名记录（布尔值）
    """
    history_list = load_history()

    """文件重命名，并记录到历史记录文件"""
    new_record_dict = {'directory': directory, 'old_name_list': [], 'new_name_list': []}
    for old_name, new_name in zip(old_name_list, new_name_list):
        if old_name == new_name:
            logging.info(f'【未更改】{old_name}')
        else:
            try:
                os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
            except FileNotFoundError:
                logging.error(f'【错误】文件“{old_name}”不存在！')
            else:
                logging.info(f'【成功】{old_name} -> {new_name}')
                if with_record_history:
                    new_record_dict['old_name_list'].append(old_name)
                    new_record_dict['new_name_list'].append(new_name)

    """将重命名记录保存至文件中"""
    if new_record_dict['new_name_list'] and with_record_history:
        history_list.append(new_record_dict)
        with open(history_file_path, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, ensure_ascii=False, indent=4)
            logging.info('新增一条重命名记录')


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
    elif rule_type == 4:
        new_name_list = use_type_4(config_dict, old_name_list)

    logging.info('已生成新文件名列表')
    return new_name_list
