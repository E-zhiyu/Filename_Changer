# file_operations/file_utils.py
import platform  # 判断系统类型
import stat  # 判断文件属性

from FilenameChanger.rename_rules.rule_manager import *

"""
功能：实现对文件的操作
"""


def is_hidden_or_is_protected(directory):
    """
    功能：获取目标路径下的所有隐藏文件（支持Windows隐藏属性）和受保护（系统文件和只读文件）的文件名
    :param directory: 目标路径
    :return: 是否为需要排除的文件文件（布尔值）
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
    :param directory: 目标路径
    :return: 旧文件名列表
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
    功能：执行重命名操作并显示重命名结果
    :param directory:目标文件夹
    :param old_name:旧文件名
    :param new_name:新文件名
    """
    if old_name == new_name:
        logger.info(f'【无法拆分】{old_name}')
        print(f'【无法拆分】{old_name}')
    else:
        try:
            os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
        except FileNotFoundError:
            logger.error(f'【错误】文件“{old_name}”不存在！')
            print(f'【错误】文件“{old_name}”不存在！')
        else:
            logger.info(f'【成功】{old_name} -> {new_name}')
            print(f'【成功】{old_name} -> {new_name}')


def generate_new_name(all_rules, old_names):
    """
    功能：根据已加载的规则生成新文件名
    返回：新文件名列表
    """
    split_char = get_the_function(all_rules)
    zipped_names = analysis_rules(all_rules, old_names)
    new_names = []
    for i in zipped_names:
        f, b, e = i  # 解包压缩的文件名

        # 去除前后空格
        if f[0] == ' ':
            f = f[1:]
        if f[-1] == ' ':
            f = f[:-1]
        if b:
            if b[0] == ' ':
                b = b[1:]
            if b[-1] == ' ':
                b = b[:-1]
            new = b + ' ' + split_char + ' ' + f + e  # 将f,b前后调换生成新文件名
        else:
            new = f + e  # 若没有第二部分文件名则保持原状
        new_names.append(new)  # 将新名字并入新文件名列表

    logger.info('已生成新文件名列表')
    return new_names
