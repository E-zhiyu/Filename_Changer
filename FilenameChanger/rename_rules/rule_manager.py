# rename_rules/rule_manager.py
"""
规则控制模块：控制有关重命名规则的操作
"""
import json, shutil
from json import JSONDecodeError

from FilenameChanger import rule_path
from FilenameChanger.log.log_recorder import *
from FilenameChanger.Fluent_Widgets_GUI.app.common.config import cfg
from FilenameChanger.database.database_connector import create_connection


def load_rule():
    """
    功能：加载配置文件
    返回：json文件根字典
    """
    if cfg.get(cfg.databaseMode):
        connection = create_connection()[0]
        if connection is None:
            return {}, False
        cursor = connection.cursor()

        """创建主表"""
        sql = """\
        CREATE TABLE IF NOT EXISTS rule_info(
            num INT NOT NULL,
            selected_index INT NOT NULL
        )"""
        cursor.execute(sql)

        """创建副表"""
        sql = """\
        CREATE TABLE IF NOT EXISTS rules(
            rule_id INT AUTO_INCREMENT PRIMARY KEY,
            type INT,
            name VARCHAR(100),
            description VARCHAR(255),
            split_char VARCHAR(50),
            enable_re BOOLEAN DEFAULT FALSE,
            new_ext VARCHAR(30),
            date_type INT,
            position VARCHAR(10),
            target_str VARCHAR(255),
            new_str VARCHAR(255),
            num_type VARCHAR(50),
            new_name VARCHAR(255),
            use_original_name BOOLEAN DEFAULT FALSE,
            action_scope TINYINT,
            rule_function TINYINT,
            start_num INT,
            step_length INT,
            date_value VARCHAR(100),
            string VARCHAR(255)
        )"""
        cursor.execute(sql)

        """查询表内容"""
        # 查询规则数量和选中的下标
        sql = 'SELECT * FROM rule_info'
        cursor.execute(sql)
        rule_info = cursor.fetchone()  # 保存一行记录

        # 建立规则根字典
        rule_dict = {
            'num': rule_info['num'] if rule_info is not None else 0,
            'selected_index': rule_info['selected_index'] if rule_info is not None else 0,
            'rules': []
        }

        # 查询规则并保存至规则根字典
        sql = """\
        SELECT type, name, description, split_char, enable_re,new_ext,
               date_type, position, target_str, new_str, num_type,
               new_name, use_original_name,action_scope, rule_function, start_num,
               step_length, date_value, string
        FROM rules
        """
        cursor.execute(sql)
        rules = cursor.fetchall()
        for rule in rules:
            rule_data = {
                "type": rule["type"],
                "name": rule["name"],
                "desc": rule["description"],
                "split_char": rule["split_char"],
                "enable_re": rule["enable_re"],
                "new_ext": rule["new_ext"],
                "date_type": rule["date_type"],
                "position": rule["position"],
                "target_str": rule["target_str"],
                "new_str": rule["new_str"],
                "num_type": rule["num_type"],
                "new_name": rule["new_name"],
                "use_original_name": rule["use_original_name"],
                "action_scope": rule["action_scope"],
                "function": rule["rule_function"],
                "start_num": rule["start_num"],
                "step_length": rule["step_length"],
                "date": rule["date_value"],
                "string": rule["string"]
            }
            # 清理空值
            rule_data = {k: v for k, v in rule_data.items() if v is not None}
            rule_dict["rules"].append(rule_data)

        connection.close()
        return rule_dict, True
    else:
        try:
            with open(rule_path, 'r', encoding='utf-8') as f:
                logging.info('加载规则配置……')
                rule_dict = json.load(f)

                if not rule_dict:  # 防止规则文件存在但是被修改为空
                    raise FileNotFoundError

                return rule_dict, True
        except (JSONDecodeError, FileNotFoundError):  # 防止规则文件被篡改为非法值
            logging.info('配置文件为空或不存在，正在初始化……')
            init_json()
            with open(rule_path, 'r', encoding='utf-8') as f:
                logging.info('规则配置已初始化并成功加载')
                return json.load(f), True


def save_new_rule(rule_dict, new_rule):
    """
    功能：将新规则并入已存在的规则列表
    参数 rule_dict：规则文件根字典
    参数 new_rule：新规则字典
    """
    rule_dict['num'] += 1
    rule_dict['rules'].append(new_rule)  # 将新规则字典并入现有的规则

    if cfg.get(cfg.databaseMode):
        connection = create_connection()[0]
        if connection is None:
            return False
        cursor = connection.cursor()

        # 更新规则数量
        sql = "UPDATE rule_info SET num=%s"
        cursor.execute(sql, rule_dict['num'])

        # 将新规则插入副表
        sql = """\
        INSERT INTO rules
        (type, name, description, split_char, enable_re, new_ext,
         date_type, position, target_str, new_str, num_type, 
         new_name, use_original_name, action_scope, rule_function, start_num,
         step_length, date_value, string)
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            new_rule.get('type'),
            new_rule.get('name'),
            new_rule.get('desc'),
            new_rule.get('split_char'),
            new_rule.get('enable_re'),
            new_rule.get('new_ext'),
            new_rule.get('date_type'),
            new_rule.get('position'),
            new_rule.get('target_str'),
            new_rule.get('new_str'),
            new_rule.get('num_type'),
            new_rule.get('new_name'),
            new_rule.get('use_original_name'),
            new_rule.get('action_scope'),
            new_rule.get('function'),
            new_rule.get('start_num'),
            new_rule.get('step_length'),
            new_rule.get('date'),
            new_rule.get('string')
        ))

        connection.commit()
        connection.close()
    else:
        with open(rule_path, 'w', encoding='utf-8') as f:
            json.dump(rule_dict, f, ensure_ascii=False, indent=4)
            logging.info('新规则已成功保存')
    return True


def revise_rule(rule_dict, revised_rule, index):
    """
    功能：修改指定下标的规则并保存
    参数 rule_dict：旧的规则字典
    参数 revised_rule：修改后的规则
    参数 index：需要修改的规则的下标
    """
    rule_dict['rules'][index] = revised_rule

    if cfg.get(cfg.databaseMode):
        connection = create_connection()[0]
        if connection is None:
            return False
        cursor = connection.cursor()

        rule_id = rule_dict['rules'][index]['rule_id']
        sql = """\
        UPDATE rules SET
        type=%s,name=%s,description=%s,split_char=%s,enable_re=%s,new_ext=%s,
        date_type=%s,position=%s,target_str=%s,new_str=%s,num_type=%s,
        new_name=%s,use_original_name=%s,action_scope=%s,rule_function=%s,start_num=%s,
        step_length=%s,date_value=%s,string=%s
        WHERE rule_id=%s
        """
        cursor.execute(sql, (
            revised_rule.get('type'),
            revised_rule.get('name'),
            revised_rule.get('desc'),
            revised_rule.get('split_char'),
            revised_rule.get('enable_re'),
            revised_rule.get('new_ext'),
            revised_rule.get('date_type'),
            revised_rule.get('position'),
            revised_rule.get('target_str'),
            revised_rule.get('new_str'),
            revised_rule.get('num_type'),
            revised_rule.get('new_name'),
            revised_rule.get('use_original_name'),
            revised_rule.get('action_scope'),
            revised_rule.get('function'),
            revised_rule.get('start_num'),
            revised_rule.get('step_length'),
            revised_rule.get('date'),
            revised_rule.get('string'),
            rule_id
        ))

        connection.commit()
        connection.close()
    else:
        with open(rule_path, 'w', encoding='utf-8') as f:
            json.dump(rule_dict, f, ensure_ascii=False, indent=4)
    return True


def init_json():
    """初始化规则文件"""
    inited_rules = {'num': 0, 'selected_index': 0, 'rules': []}
    os.makedirs(os.path.dirname(rule_path), exist_ok=True)  # 先创建规则文件目录
    with open(rule_path, 'w', encoding='utf-8') as f:
        json.dump(inited_rules, f, ensure_ascii=False, indent=4)

    logging.info('规则文件初始化成功')


def del_rules(rule_dict, index):
    """
    功能：删除指定的规则
    参数 rule_dict：规则配置文件根字典
    参数 index：需要删除的规则的下标
    """
    if rule_dict['num'] == 1:
        logging.warning('无法删除最后一个规则')
        return False, '无法删除最后一个规则'
    else:
        if cfg.get(cfg.databaseMode):
            connection = create_connection()[0]
            if connection is None:
                logging.error('无法删除：连接至数据库时出错')
                return False, '连接至数据库时出错'

        logging.info(f'正在删除第{index + 1}个规则，剩余规则{rule_dict['num'] - 1}个')

        if index == rule_dict['selected_index']:  # 判断删除的规则是否被选中，删除被选中的规则则改为选中第一个规则
            logging.info(f'第{index + 1}个规则为激活的规则，更改为激活第一个规则')
            rule_dict['selected_index'] = 0
        elif index < rule_dict['selected_index']:  # 若删除的规则下标小于选中的规则，则将selected_index-1
            rule_dict['selected_index'] -= 1

        # 将规则数-1
        rule_dict['num'] -= 1

        if cfg.get(cfg.databaseMode):
            cursor = connection.cursor()

            sql = 'UPDATE rule_info SET num=%s, selected_index=%s'
            cursor.execute(sql, rule_dict['num'], rule_dict['selected_index'])

            rule_id = rule_dict['rules'][index]['rule_id']
            sql = 'DELETE FROM rules WHERE rule_id=%s'
            cursor.execute(sql, rule_id)

            del rule_dict['rules'][index]

            connection.commit()
            connection.close()
        else:
            del rule_dict['rules'][index]
            with open(rule_path, 'w', encoding='utf-8') as f:
                json.dump(rule_dict, f, ensure_ascii=False, indent=4)

        logging.info('规则删除成功')
        return True, '已成功删除选中的规则'


def activate_rule(config_dict, index):
    """
    功能：激活指定的规则
    参数 config_dict：规则配置文件根字典
    参数 index：需要切换到的规则的下标
    """
    logging.info(f'用户激活规则{index + 1}')
    config_dict['selected_index'] = index

    if cfg.get(cfg.databaseMode):
        connection = create_connection()[0]
        if connection is None:
            logging.error('无法激活：连接至数据库时出错')
            return False
        cursor = connection.cursor()

        sql = 'UPDATE rule_info SET selected_index=%s'
        cursor.execute(sql, config_dict['selected_index'])

        connection.commit()
        connection.close()
    else:
        with open(rule_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)

    logging.info('规则激活成功')
    return True


def import_rule(src_path):
    """
    功能：导入外部规则文件
    参数 src_path：导入的规则文件路径
    返回：导入结果和提示语
    """

    class FileSafeCopier:
        """文件安全复制器"""

        def __init__(self, path):
            self.src_path = path  # 源文件位置

        def safeCopy(self):
            """安全复制"""
            try:
                with open(self.src_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, dict) and self.__content_verify(content):
                        if cfg.get(cfg.databaseMode):
                            connection = create_connection()[0]
                            if connection is None:
                                return False, '连接至数据库时出错'
                            cursor = connection.cursor()

                            # 读取文件内容
                            with open(src_path, 'r', encoding='utf-8') as f:
                                rule_dict = json.load(f)

                            # 更新主表
                            sql = 'DELETE FROM rule_info'
                            cursor.execute(sql)

                            num = rule_dict['num']
                            selected_index = rule_dict['selected_index']
                            sql = 'INSERT INTO rule_info (num,selected_index) VALUES (%s, %s)'
                            cursor.execute(sql, (num, selected_index))

                            # 更新副表
                            sql = 'DELETE FROM rules'
                            cursor.execute(sql)

                            for rule in rule_dict['rules']:
                                sql = """\
                                INSERT INTO rules 
                                    (type, name, description, split_char, enable_re, new_ext,
                                     date_type, position, target_str, new_str, num_type, 
                                     new_name, use_original_name, action_scope, rule_function, start_num,
                                     step_length, date_value, string)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                                cursor.execute(sql, (
                                    rule.get('type'),
                                    rule.get('name'),
                                    rule.get('desc'),
                                    rule.get('split_char'),
                                    rule.get('enable_re'),
                                    rule.get('new_ext'),
                                    rule.get('date_type'),
                                    rule.get('position'),
                                    rule.get('target_str'),
                                    rule.get('new_str'),
                                    rule.get('num_type'),
                                    rule.get('new_name'),
                                    rule.get('use_original_name'),
                                    rule.get('action_scope'),
                                    rule.get('function'),
                                    rule.get('start_num'),
                                    rule.get('step_length'),
                                    rule.get('date'),
                                    rule.get('string'),
                                ))

                            connection.commit()
                            connection.close()
                        else:
                            shutil.copy(self.src_path, rule_path)
                    else:
                        raise ValueError
            except JSONDecodeError:
                return False, '不是有效的JSON格式'
            except FileNotFoundError:
                return False, '待导入的文件不存在或被移除'
            except ValueError:
                return False, '文件内容格式错误'
            else:
                return True, '规则导入成功'

        @staticmethod
        def __content_verify(content):
            """验证导入的规则文件内容是否符合规范"""
            num = content.get('num')
            selected_index = content.get('selected_index')
            rules = content.get('rules')
            if not (isinstance(num, int) and isinstance(selected_index, int) and isinstance(rules, list)):
                return False
            elif len(rules) != num:
                return False
            elif selected_index < 0 or selected_index >= num:
                return False
            else:
                return True

    safeCopier = FileSafeCopier(src_path)
    return safeCopier.safeCopy()


def export_rule(dst_path):
    """
    功能：导出规则文件到指定位置
    参数 dst_path：导出到的文件夹路径
    返回：导出结果和提示语
    """
    if cfg.get(cfg.databaseMode):
        rule_dict, flag = load_rule()
        if not flag:
            return False, '连接至数据库时出错'

        # 去除rule_id键值对
        for rule in rule_dict['rules']:
            try:
                del rule['rule_id']
            except KeyError:
                pass

        with open(dst_path, 'w', encoding='utf-8') as f:
            json.dump(rule_dict, f, ensure_ascii=False, indent=4)
        return True, '规则导出成功'
    else:
        try:
            shutil.copy(rule_path, dst_path)
        except FileNotFoundError:
            return False, '规则文件不存在或被移除'
        else:
            return True, '规则导出成功'
