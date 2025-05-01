import json
from json import JSONDecodeError

from FilenameChanger.file_operations.file_utils import rename_files
from FilenameChanger.log.log_recorder import *
from FilenameChanger import history_file_path


def load_history():
    """
    获取已保存的历史记录
    返回：历史记录列表
    """
    # 创建历史记录文件夹
    if not os.path.isdir(os.path.dirname(history_file_path)):
        os.mkdir(os.path.dirname(history_file_path))

    # 读取现有历史记录
    try:
        with open(history_file_path, 'r', encoding='utf-8') as f:
            logging.info('成功读取已保存的历史记录')
            history_list = json.load(f)
    except (FileNotFoundError, JSONDecodeError):
        with open(history_file_path, 'w', encoding='utf-8') as f:
            logging.info('历史记录文件不存在，正在初始化……')
            history_list = []
            json.dump(history_list, f, ensure_ascii=False, indent=4)
            logging.info('历史记录文件初始化成功')

    return history_list


def cancel_rename_operation():
    """
    功能：撤销上一次重命名操作
    """
    # 加载已保存的历史记录
    history_list = load_history()

    # 判断历史记录是否为空
    if not history_list:
        logging.error('历史记录为空，无法撤销重命名')
        return 0

    # 加载上一次的重命名记录
    last_history_dict = history_list.pop()
    old_name_list = last_history_dict['old_name_list']  # 加载旧文件名列表
    new_name_list = last_history_dict['new_name_list']  # 加载新文件名列表
    directory = last_history_dict['directory']  # 加载目标文件夹路径

    # 判断旧文件夹路径是否可用
    if not os.path.isdir(directory):
        logging.error('无法撤销：旧文件夹路径无效')
        return -1  # 若历史记录中的文件夹不存在，则不会执行下面的文件写入操作，无需担心历史记录被删除

    # 删除最近一条重命名记录
    if not os.path.isdir(os.path.dirname(history_file_path)):  # 若该记录对应的文件夹被删除则不将删除一条记录的列表覆写到文件中
        os.mkdir(os.path.dirname(history_file_path))
    with open(history_file_path, 'w', encoding='utf-8') as f:
        json.dump(history_list, f, ensure_ascii=False, indent=4)

    # 撤销上一次重命名
    logging.info('开始撤销重命名……')
    rename_files(directory, new_name_list, old_name_list, False)  # 把新旧文件名反过来

    return 1
