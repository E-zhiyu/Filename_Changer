# file_history_operations/file_history_operations.py
"""
文件和历史记录操作模块：控制有关待重命名文件和历史记录的各种操作
"""
import platform  # 判断系统类型
import stat  # 判断文件属性

from FilenameChanger import history_file_path
from FilenameChanger.rename_rules.rule_applier import *

from FilenameChanger.Fluent_Widgets_GUI.app.common.config import cfg
from FilenameChanger.database.database_connector import create_connection


def is_directory_usable(directory: str):
    """
    功能：判断文件夹路径是否有效
    参数 directory：目标文件夹路径
    返回：判断结果和消息
    """
    if directory:
        # 路径有效性的异常处理
        if os.path.isdir(directory):
            return True, '路径有效'
        else:
            return False, '路径无效'
    else:
        return False, '用户清空路径'


def hidden_or_protected(path: str):
    """
    功能：获取目标路径下的所有隐藏文件（支持Windows隐藏属性）和受保护（系统文件和只读文件）的文件名
    参数 path：待判断的对象的路径
    返回：是否为需要排除的文件文件（布尔值）
    """
    name = os.path.basename(path)
    if name.startswith('.'):  # 若文件名以'.'开头则直接判断为隐藏文件
        return True
    if platform.system() == 'Windows':
        try:
            # 获取 Windows 文件属性标志位
            attrs = os.stat(path).st_file_attributes
            # 检查是否隐藏（0x2）或系统文件（0x4）
            if attrs & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM):
                logging.debug(f'排除隐藏文件或系统文件：“{path}”')
                return True
            # 排除只读文件（0x1）
            if attrs & stat.FILE_ATTRIBUTE_READONLY:
                logging.debug(f'排除只读文件：{path}')
                return True
        except (AttributeError, OSError):
            pass  # 非 Windows 或文件不可访问
    return False


def scan_files(directory: str) -> list:
    """
    功能：扫描目标路径的所有文件名
    参数 directory：目标路径
    返回：旧文件名列表
    """
    folder_mode = cfg.get(cfg.folderMode)
    secureScanning = cfg.get(cfg.secureScanning)
    logging.info('获取文件名列表中……')

    if folder_mode:
        if secureScanning:
            old_name = [folder for folder in os.listdir(directory) if
                        os.path.isdir(os.path.join(directory, folder)) and not hidden_or_protected(
                            os.path.join(directory, folder))]
        else:
            old_name = [folder for folder in os.listdir(directory) if
                        os.path.isdir(os.path.join(directory, folder))]
    else:
        if secureScanning:
            old_name = [file for file in os.listdir(directory) if
                        os.path.isfile(os.path.join(directory, file)) and not hidden_or_protected(
                            os.path.join(directory, file))]
        else:
            old_name = [file for file in os.listdir(directory) if
                        os.path.isfile(os.path.join(directory, file))]

    if not old_name:
        logging.warning('文件名获取失败：目标文件夹不存在或为空')
        return []
    else:
        logging.info('文件名列表获取成功')
        return old_name


def rename_operation(directory: str, old_names: tuple):
    """
    功能：执行“文件重命名”操作
    参数 directory：目标文件夹路径
    参数 old_names：旧文件名序列
    返回：重命名是否正常结束、重命名提示消息、新历史记录字典
    """
    if not old_names:
        logging.info(f'文件夹：“{directory}”为空')
        return False, '文件夹为空或未选择任何文件', {}

    config_dict, flag = load_rule()  # 重命名时加载已保存的规则
    if flag and not config_dict['rules']:  # 若读取成功但是规则为空，则结束本函数
        logging.warning('规则为空，请先前往规则设置写入规则')
        return False, '规则为空，请先前往规则设置写入规则！', {}
    elif not flag:
        logging.error('规则读取失败：数据库连接超时')
        return False, '规则读取失败：数据库连接超时！', {}

    selected_rule = config_dict['rules'][config_dict['selected_index']]
    logging.info(
        f'当前活跃的规则为“规则{config_dict['selected_index'] + 1}”，'
        f'规则种类：{selected_rule['type']}')

    new_name_list = get_new_name_list(selected_rule, old_names, directory)  # 生成新文件名

    logging.info('开始文件重命名……')
    if not new_name_list:
        logging.fatal('严重错误：新文件名列表为空')
        return False, '严重错误：新文件名列表为空', {}

    flag, success, fail, new_history_dict = rename_files(directory, old_names, new_name_list)  # 执行重命名操作
    if flag:
        logging.info(f'重命名结束，成功：{success}个，失败：{fail}个')
        return True, f'重命名结束，成功：{success}个，失败：{fail}个', new_history_dict
    else:
        logging.error('重命名失败：数据库连接超时')
        return False, '重命名失败，数据库连接超时', {}


def rename_files(directory: str, old_names: (tuple, list), new_name_list: list, record_history: bool = True):
    """
    功能：执行重命名操作并新增历史记录
    参数 directory：目标文件夹
    参数 old_names：被替换的文件名序列
    参数 new_name_list：新文件名序列
    参数 with_record_history：是否记录重命名记录
    """
    logging.info('进行文件名修改操作中……')
    history_list = load_history()

    folder_mode = cfg.get(cfg.folderMode)
    database_mode = cfg.get(cfg.databaseMode)

    """启用数据库模式时先创建数据库连接"""
    if database_mode:
        connection = create_connection()[0]
        if connection is None:
            logging.error('重命名失败，数据库连接超时')
            return False, 0, 0, {}

    """文件重命名"""
    new_history_dict = {'directory': directory, 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'old_name_list': [], 'new_name_list': [], 'error_files': [], 'folder_mode': folder_mode}
    for old_name, new_name in zip(old_names, new_name_list):
        if old_name == new_name:
            logging.info(f'【未更改】{old_name}')
            new_history_dict['error_files'].append(f'【前后文件名相同】{old_name}')
        else:
            try:
                os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
            except FileNotFoundError:
                logging.error(f'【错误】文件“{old_name}”不存在')
                new_history_dict['error_files'].append(f'【文件不存在】{old_name}')
            except FileExistsError:
                logging.error(f'【错误】文件“{old_name}”重命名后将导致重名')
                new_history_dict['error_files'].append(f'【文件重名】{old_name}')
            except PermissionError:
                logging.error(f'【文件被占用】文件“{old_name}”被其他程序占用')
                new_history_dict['error_files'].append(f'【文件被占用】{old_name}')
            except (OSError, WindowsError):
                logging.error(f'【文件名语法错误】新文件名中含有非法字符')
                new_history_dict['error_files'].append(f'【文件名语法错误】“{new_name}”中含有非法字符')
            else:
                logging.info(f'【成功】{old_name} -> {new_name}')
                if record_history:
                    new_history_dict['old_name_list'].append(old_name)
                    new_history_dict['new_name_list'].append(new_name)

    """保存重命名历史记录"""
    if (new_history_dict['new_name_list'] or new_history_dict['error_files']) and record_history:
        if database_mode:
            cursor = connection.cursor()

            # 将内容插入主表
            sql = """
            INSERT INTO history 
            (directory, time, folder_mode)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (directory, new_history_dict['time'], folder_mode))
            operation_id = cursor.lastrowid  # 获取刚插入的主表ID
            new_history_dict['operation_id'] = operation_id  # 数据库模式下需要记录重命名操作的ID

            # 保存修改的文件
            for old, new in zip(old_names, new_name_list):
                sql = f"""\
                INSERT INTO changed_files
                (operation_id, old_name, new_name)
                VALUES (%s, %s, %s)"""
                cursor.execute(sql, (operation_id, old, new))

            # 保存出错的文件
            for error_file in new_history_dict['error_files']:
                sql = f"""\
                INSERT INTO error_files
                (operation_id, reasonAndName)
                VALUES (%s, %s)"""
                cursor.execute(sql, (operation_id, error_file))

            connection.commit()
            connection.close()
        else:
            history_list.insert(0, new_history_dict)
            with open(history_file_path, 'w', encoding='utf-8') as f:
                json.dump(history_list, f, ensure_ascii=False, indent=4)
        logging.info('新增的历史记录已保存')

    # 统计成功和失败的文件数
    fail = len(new_history_dict['error_files'])
    success = len(old_names) - fail
    return True, success, fail, new_history_dict  # 返回成功重命名和重命名时出错的文件数，以及新增加的历史记录


def get_new_name_list(selected_rule: dict, old_names: (tuple, list), directory: str):
    """
    功能：根据已加载的规则生成新文件名
    参数 selected_rule：当前激活的规则
    参数 old_names：旧文件名序列
    参数 directory：目标文件夹路径
    返回：新文件名列表
    """
    rule_type = selected_rule['type']

    if rule_type == 1:
        new_name_list = use_type_1(selected_rule, old_names)
    elif rule_type == 2:
        new_name_list = use_type_2(selected_rule, old_names)
    elif rule_type == 3:
        new_name_list = use_type_3(selected_rule, old_names)
    elif rule_type == 4:
        new_name_list = use_type_4(selected_rule, old_names, directory)
    elif rule_type == 5:
        new_name_list = use_type_5(selected_rule, old_names)
    elif rule_type == 6:
        new_name_list = use_type_6(selected_rule, old_names)
    elif rule_type == 7:
        new_name_list = use_type_7(selected_rule, old_names)
    else:
        new_name_list = []  # 正常情况不会触发该语句

    logging.info('已生成新文件名列表')
    return new_name_list


def load_history() -> list:
    """
    获取已保存的历史记录
    返回：历史记录列表
    """
    logging.info('正在读取历史记录……')

    if cfg.get(cfg.databaseMode):
        connection = create_connection()[0]
        if connection is None:  # 连接出错则返回空列表
            logging.error('读取失败：数据库连接超时')
            return []
        cursor = connection.cursor()

        """表格不存在时创建空白表格"""
        # 创建历史记录主表
        sql = """\
        CREATE TABLE IF NOT EXISTS history (
            operation_id INT AUTO_INCREMENT PRIMARY KEY,  # 历史记录的自增主键，用于快速查找其对应的文件名
            directory VARCHAR(255)  NOT NULL ,
            time DATETIME,
            folder_mode BOOLEAN DEFAULT FALSE
        );"""
        cursor.execute(sql)

        # 创建更改的文件表格
        sql = """\
        CREATE TABLE IF NOT EXISTS changed_files (
            operation_id INT,
            old_name VARCHAR(255),
            new_name VARCHAR(255)
        )"""
        cursor.execute(sql)

        # 创建出错的文件表格
        sql = """\
        CREATE TABLE IF NOT EXISTS error_files (
            operation_id INT,
            reasonAndName VARCHAR(255)
        )"""
        cursor.execute(sql)

        """读取历史记录"""
        sql = 'SELECT * FROM history ORDER BY time'  # 按照时间先后顺序排序
        cursor.execute(sql)
        fetched_histories = cursor.fetchall()

        history_list = []  # 存放所有历史记录的列表
        # 循环读取所有历史记录
        for history in fetched_histories:
            operation_id = history['operation_id']
            one_history_record = {
                'operation_id': operation_id,
                'directory': history['directory'],
                'time': str(history['time']),
                'folder_mode': history['folder_mode'],
            }  # 新建一条历史记录的字典

            # 查询变化的文件
            sql = 'SELECT * FROM changed_files WHERE operation_id=%s'
            cursor.execute(sql, operation_id)
            records = cursor.fetchall()

            old_name_list = []
            new_name_list = []
            for record in records:
                old_name_list.append(record['old_name'])
                new_name_list.append(record['new_name'])
            one_history_record['old_name_list'] = old_name_list
            one_history_record['new_name_list'] = new_name_list

            # 查询出错的文件
            sql = 'SELECT * FROM error_files WHERE operation_id=%s'
            cursor.execute(sql, operation_id)
            records = cursor.fetchall()

            error_files = []
            for record in records:
                error_files.append(record['reasonAndName'])
            one_history_record['error_files'] = error_files

            # 将本次查询到的历史记录合并至历史记录列表
            history_list.insert(0, one_history_record)

        connection.close()
    else:
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
    """撤销上一次重命名操作"""
    history_list = load_history()  # 加载已保存的历史记录

    # 判断历史记录是否为空
    if not history_list:
        logging.warning('历史记录为空，无法撤销重命名')
        return False, '历史记录为空，无法撤销重命名'

    # 加载上一次的重命名记录
    last_history_dict = history_list[0]
    old_name_list = last_history_dict['old_name_list']  # 加载旧文件名列表
    new_name_list = last_history_dict['new_name_list']  # 加载新文件名列表
    directory = last_history_dict['directory']  # 加载目标文件夹路径

    # 判断旧文件夹路径是否可用
    if not os.path.isdir(directory):
        logging.warning('无法撤销：旧文件夹路径无效')
        return False, '无法撤销：旧文件夹路径无效'  # 提前返回，目的是不修改历史记录文件

    # 撤销上一次重命名
    logging.info('开始撤销重命名……')
    flag = rename_files(directory, new_name_list, old_name_list, False)[0]  # 把新旧文件名反过来
    if flag:
        logging.info('撤销重命名成功')
        return True, '已成功撤销重命名'
    else:
        logging.error('无法撤销，数据库连接超时')
        return False, '无法撤销，数据库连接超时'


def clear_history():
    """清除所有历史记录"""
    if cfg.get(cfg.databaseMode):
        connection = create_connection()[0]
        if connection is None:
            logging.error('清除失败：数据库连接超时')
            return False

        cursor = connection.cursor()
        sql = 'DELETE FROM history'
        cursor.execute(sql)
        sql = 'DELETE FROM changed_files'
        cursor.execute(sql)
        sql = 'DELETE FROM error_files'
        cursor.execute(sql)

        connection.commit()
        connection.close()
    else:
        logging.info('历史记录已清空')
        with open(history_file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    return True


def history_del(history_list: list, index: int):
    """
    功能：删除指定下标的历史记录
    参数 history_list：历史记录列表
    参数 index：指定删除的历史记录下标
    """
    if cfg.get(cfg.databaseMode):
        connection = create_connection()[0]
        if connection is None:
            logging.error('删除失败：数据库连接超时')
            return False

        cursor = connection.cursor()
        operation_id = history_list[index]['operation_id']
        del history_list[index]

        # 删除主表数据
        sql = 'DELETE FROM history WHERE operation_id=%s'
        cursor.execute(sql, operation_id)

        # 删除修改的文件记录
        sql = 'DELETE FROM changed_files WHERE operation_id=%s'
        cursor.execute(sql, operation_id)

        # 删除出错的文件记录
        sql = 'DELETE FROM error_files WHERE operation_id=%s'
        cursor.execute(sql, operation_id)

        connection.commit()
        connection.close()
    else:
        del history_list[index]
        if not os.path.isdir(os.path.dirname(history_file_path)):
            os.mkdir(os.path.dirname(history_file_path))  # 防止历史记录文件夹被移除
        with open(history_file_path, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, ensure_ascii=False, indent=4)

    logging.info(f'已删除历史记录，下标：{index}')
    return True
