# rename_rules/rule_manager.py
import json
from json import JSONDecodeError

from FilenameChanger import config_path
from FilenameChanger.log.log_recorder import *

"""
规则文件模块：控制所有有关命名规则文件的操作
"""


def load_config():
    """
    功能：加载配置文件
    返回：json文件根字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            logging.info('加载规则配置……')
            config = json.load(f)

            if not config:  # 防止规则文件存在但是被修改为空
                raise FileNotFoundError

            return config
    except (JSONDecodeError, FileNotFoundError):  # 防止规则文件存在但是为空而导致程序无法启动
        logging.info('配置文件为空或不存在，正在初始化……')
        init_json()
        with open(config_path, 'r', encoding='utf-8') as f:
            logging.info('规则配置已初始化并成功加载')
            return json.load(f)


def save_new_rule(config_dict, new_rule):
    """
    功能：将新规则并入已存在的规则列表
    参数 config_dict：规则配置文件根字典
    参数 new_rule：新规则字典
    """
    config_dict['num'] += 1
    config_dict['rules'].append(new_rule)  # 将新规则字典并入现有的规则

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=4)
        logging.info('新规则已成功保存')


def revise_rule(rule_dict, revised_rule, index):
    """
    功能：修改指定下标的规则并保存
    参数 rule_dict：旧的规则字典
    参数 revised_rule：修改后的规则列表
    参数 index：需要修改的规则的下标
    """
    rule_dict['rules'][index] = revised_rule
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(rule_dict, f, ensure_ascii=False, indent=4)


def init_json():
    """
    功能：在没有规则文件或者规则文件为空的前提下初始化规则文件
    参数 config_path：规则配置文件路径
    """
    inited_rules = {'num': 0, 'selected_index': 0, 'rules': []}
    os.makedirs(os.path.dirname(config_path), exist_ok=True)  # 先创建规则文件目录
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(inited_rules, f, ensure_ascii=False, indent=4)

    logging.info('规则文件初始化成功')


def del_rules(config_dict, index):
    """
    功能：删除指定的规则
    参数 config_dict：规则配置文件根字典
    参数 index：需要删除的规则的下标
    """
    if config_dict['num'] == 1:
        logging.error('无法移除最后一个规则')
        return 0
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
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)

        return 1


def switch_rule(config_dict, index):
    """
    功能：切换需要加载的规则
    参数 config_dict：规则配置文件根字典
    参数 index：需要切换到的规则的下标
    """
    logging.info(f'用户切换至规则{index + 1}')
    config_dict['selected_index'] = index
    # 将更改写入配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=4)


def analise_rule(addRuleWindow):
    """
    功能：解析用户输入的规则参数
    参数 addRuleWindow：添加规则的窗口
    返回：解析的规则字典
    """
    logging.info(f'规则类型：{addRuleWindow.new_rule_type}')
    logging.info(f'名称：{addRuleWindow.ruleNameLineEdit.text()}')
    logging.info(f'描述：{addRuleWindow.ruleDescLineEdit.text()}')

    if addRuleWindow.new_rule_type == 1:
        rule = {
            'type': 1,
            'name': addRuleWindow.ruleNameLineEdit.text(),
            'desc': addRuleWindow.ruleDescLineEdit.text(),
            'split_char': addRuleWindow.new_control['splitCharLineEdit'].text()
        }
        logging.info(f'分隔符：{addRuleWindow.new_control["splitCharLineEdit"].text()}')
    elif addRuleWindow.new_rule_type == 2:
        rule = {
            'type': 2,
            'name': addRuleWindow.ruleNameLineEdit.text(),
            'desc': addRuleWindow.ruleDescLineEdit.text(),
            'new_ext': addRuleWindow.new_control['extLineEdit'].text()
        }
        logging.info(f'新扩展名：{addRuleWindow.new_control["extLineEdit"].text()}')
    elif addRuleWindow.new_rule_type == 3:
        rule = {
            'type': 3,
            'name': addRuleWindow.ruleNameLineEdit.text(),
            'desc': addRuleWindow.ruleDescLineEdit.text(),
            'target_str': addRuleWindow.new_control['oldStrLineEdit'].text(),
            'use_re': addRuleWindow.new_control['useReCheckBox'].isChecked(),
            'new_str': addRuleWindow.new_control['newStrLineEdit'].text()
        }
        logging.info(f'匹配字符串：{addRuleWindow.new_control["oldStrLineEdit"].text()}')
        logging.info(f'使用正则表达式：{addRuleWindow.new_control['useReCheckBox'].isChecked()}')
        logging.info(f'新字符串：{addRuleWindow.new_control["newStrLineEdit"].text()}')
    elif addRuleWindow.new_rule_type == 4:
        rule = {
            'type': 4,
            'name': addRuleWindow.ruleNameLineEdit.text(),
            'desc': addRuleWindow.ruleDescLineEdit.text(),
            'split_char': addRuleWindow.new_control['splitCharLineEdit'].text()
        }
        logging.info(f'分隔符：{addRuleWindow.new_control["splitCharLineEdit"].text()}')

        if addRuleWindow.new_control['headBtn'].isChecked():
            rule['position'] = 'head'
            logging.info(f'位置：头部')
        elif addRuleWindow.new_control['tailBtn'].isChecked():
            rule['position'] = 'tail'
            logging.info(f'位置：尾部')

        if addRuleWindow.new_control['sysDateBtn'].isChecked():
            rule['date'] = None
            logging.info('日期：动态填充系统日期')
        else:
            rule['date'] = addRuleWindow.new_control['customDateLineEdit'].text()
            logging.info(f'日期：{addRuleWindow.new_control["customDateLineEdit"].text()}')
    elif addRuleWindow.new_rule_type == 5:
        rule = {
            'type': 5,
            'name': addRuleWindow.ruleNameLineEdit.text(),
            'desc': addRuleWindow.ruleDescLineEdit.text(),
            'new_name': addRuleWindow.new_control['newNameLineEdit'].text(),
            'num_type': addRuleWindow.new_control['numTypeComboBox'].text(),
        }
        logging.info(f'新文件名：{addRuleWindow.new_control['newNameLineEdit'].text()}')
        logging.info(f'编号样式：{addRuleWindow.new_control['numTypeComboBox'].text()}')

        if not addRuleWindow.new_control['startNumLineEdit'].text():
            rule['start_num'] = 1
        else:
            rule['start_num'] = int(addRuleWindow.new_control['startNumLineEdit'].text())
        logging.info(f'起始编号：{rule['start_num']}')

        if not addRuleWindow.new_control['stepLengthLineEdit'].text():
            rule['step_length'] = 1
        else:
            rule['step_length'] = int(addRuleWindow.new_control['stepLengthLineEdit'].text())
        logging.info(f'步长：{rule['step_length']}')

        if addRuleWindow.new_control['headBtn'].isChecked():
            rule['position'] = 'head'
            logging.info(f'位置：头部')
        elif addRuleWindow.new_control['tailBtn'].isChecked():
            rule['position'] = 'tail'
            logging.info(f'位置：尾部')

    return rule
