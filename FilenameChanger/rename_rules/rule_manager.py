# rename_rules/rule_manager.py
"""
规则控制模块：控制有关重命名规则的操作
"""
import json, shutil
from json import JSONDecodeError

from FilenameChanger.Fluent_Widgets_GUI.app.common.config import cfg
from FilenameChanger import rule_path
from FilenameChanger.log.log_recorder import *


def load_rule():
    """
    功能：加载配置文件
    返回：json文件根字典
    """
    if cfg.get(cfg.databaseMode):
        pass
    else:
        try:
            with open(rule_path, 'r', encoding='utf-8') as f:
                logging.info('加载规则配置……')
                rule_dict = json.load(f)

                if not rule_dict:  # 防止规则文件存在但是被修改为空
                    raise FileNotFoundError

                return rule_dict
        except (JSONDecodeError, FileNotFoundError):  # 防止规则文件被篡改为非法值
            logging.info('配置文件为空或不存在，正在初始化……')
            init_json()
            with open(rule_path, 'r', encoding='utf-8') as f:
                logging.info('规则配置已初始化并成功加载')
                return json.load(f)


def save_new_rule(rule_dict, new_rule):
    """
    功能：将新规则并入已存在的规则列表
    参数 rule_dict：规则文件根字典
    参数 new_rule：新规则字典
    """
    rule_dict['num'] += 1
    rule_dict['rules'].append(new_rule)  # 将新规则字典并入现有的规则

    with open(rule_path, 'w', encoding='utf-8') as f:
        json.dump(rule_dict, f, ensure_ascii=False, indent=4)
        logging.info('新规则已成功保存')


def revise_rule(rule_dict, revised_rule, index):
    """
    功能：修改指定下标的规则并保存
    参数 rule_dict：旧的规则字典
    参数 revised_rule：修改后的规则
    参数 index：需要修改的规则的下标
    """
    rule_dict['rules'][index] = revised_rule
    with open(rule_path, 'w', encoding='utf-8') as f:
        json.dump(rule_dict, f, ensure_ascii=False, indent=4)


def init_json():
    """
    功能：在没有规则文件或者规则文件为空的前提下初始化规则文件
    参数 config_path：规则配置文件路径
    """
    inited_rules = {'num': 0, 'selected_index': 0, 'rules': []}
    os.makedirs(os.path.dirname(rule_path), exist_ok=True)  # 先创建规则文件目录
    with open(rule_path, 'w', encoding='utf-8') as f:
        json.dump(inited_rules, f, ensure_ascii=False, indent=4)

    logging.info('规则文件初始化成功')


def del_rules(config_dict, index):
    """
    功能：删除指定的规则
    参数 config_dict：规则配置文件根字典
    参数 index：需要删除的规则的下标
    """
    if config_dict['num'] == 1:
        logging.warning('无法删除最后一个规则')
        return False, '无法删除最后一个规则'
    else:
        logging.info(f'用户删除第{index + 1}个规则，剩余规则{config_dict['num'] - 1}个')

        # 判断删除的规则是否被选中，删除被选中的规则则改为选中第一个规则
        if config_dict['selected_index'] == index and index != 0:  # 当删除第一个规则时仍然默认选中第一个规则
            logging.info(f'第{index + 1}个规则为激活的规则，更改为激活第一个规则')
            config_dict['selected_index'] = 0

        # 若删除的规则下标小于选中的规则，则将selected_index-1
        if index < config_dict['selected_index']:
            config_dict['selected_index'] -= 1

        config_dict['num'] -= 1
        del config_dict['rules'][index]
        with open(rule_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)

        return True, '已成功删除选中的规则'


def activate_rule(config_dict, index):
    """
    功能：激活指定的规则
    参数 config_dict：规则配置文件根字典
    参数 index：需要切换到的规则的下标
    """
    logging.info(f'用户激活规则{index + 1}')
    config_dict['selected_index'] = index
    # 将更改写入配置文件
    with open(rule_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=4)


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
            """安全复制的方法"""
            try:
                with open(self.src_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        if self.__content_verify(content):
                            shutil.copy(self.src_path, rule_path)
                        else:
                            raise ValueError
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

    validator = FileSafeCopier(src_path)
    return validator.safeCopy()


def export_rule(dst_path):
    """
    功能：导出规则文件到指定位置
    参数 dst_path：导出到的文件夹路径
    返回：导出结果和提示语
    """
    try:
        shutil.copy(rule_path, dst_path)
    except FileNotFoundError:
        return False, '规则文件不存在或被移除'
    else:
        return True, '规则导出成功'
