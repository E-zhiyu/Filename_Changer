# rename_rules/rule_manager.py
import json, shutil
from json import JSONDecodeError

from FilenameChanger import rule_path
from FilenameChanger.log.log_recorder import *

"""
规则文件模块：控制所有有关命名规则文件的操作
"""


def load_rule():
    """
    功能：加载配置文件
    返回：json文件根字典
    """
    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            logging.info('加载规则配置……')
            config = json.load(f)

            if not config:  # 防止规则文件存在但是被修改为空
                raise FileNotFoundError

            return config
    except (JSONDecodeError, FileNotFoundError):  # 防止规则文件存在但是为空而导致程序无法启动
        logging.info('配置文件为空或不存在，正在初始化……')
        init_json()
        with open(rule_path, 'r', encoding='utf-8') as f:
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

    with open(rule_path, 'w', encoding='utf-8') as f:
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
        logging.error('无法删除最后一个规则')
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
        with open(rule_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)

        return 1


def switch_rule(config_dict, index):
    """
    功能：切换需要加载的规则
    参数 config_dict：规则配置文件根字典
    参数 index：需要切换到的规则的下标
    """
    logging.info(f'用户激活规则{index + 1}')
    config_dict['selected_index'] = index
    # 将更改写入配置文件
    with open(rule_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=4)


def analise_rule(addRuleWindow):
    """
    功能：解析用户输入的规则参数
    参数 addRuleWindow：添加规则的窗口
    返回：解析的规则字典
    """
    rule = {
        'type': addRuleWindow.new_rule_type,
        'name': addRuleWindow.ruleNameLineEdit.text(),
        'desc': addRuleWindow.ruleDescLineEdit.text(),
    }
    logging.info(f'规则类型：{rule["type"]}')
    logging.info(f'名称：{rule["name"]}')
    logging.info(f'描述：{rule["desc"] if rule["desc"] else "<空>"}')

    if rule['type'] == 1:
        rule['split_char'] = addRuleWindow.splitCharLineEdit.text()
        logging.info(f'分隔符：{rule['split_char']}')

        rule['enable_re'] = addRuleWindow.enableReCheckBox.isChecked()
        if rule['enable_re']:
            logging.info('使用正则表达式：是')
        else:
            logging.info('使用正则表达式：否')

    elif rule['type'] == 2:
        rule['new_ext'] = addRuleWindow.extLineEdit.text()
        logging.info(f'新扩展名：{rule['new_ext']}')

    elif rule['type'] == 3:
        rule['target_str'] = addRuleWindow.oldStrLineEdit.text()
        logging.info(f'匹配字符串：{rule['target_str']}')

        rule['enable_re'] = addRuleWindow.useReCheckBox.isChecked()
        if rule['enable_re']:
            logging.info('使用正则表达式：是')
        else:
            logging.info('使用正则表达式：否')

        rule['new_str'] = addRuleWindow.newStrLineEdit.text()
        logging.info(f'新字符串：{rule['new_str']}')

    elif rule['type'] == 4:
        rule['date_type'] = addRuleWindow.dateTypeComboBox.currentIndex()
        logging.info(f'日期种类：{rule['date_type']}')

        if addRuleWindow.posLayout.headBtn.isChecked():
            rule['position'] = 'head'
            logging.info(f'位置：头部')
        elif addRuleWindow.posLayout.tailBtn.isChecked():
            rule['position'] = 'tail'
            logging.info(f'位置：尾部')

        if addRuleWindow.dateTypeComboBox.currentIndex() == 4:
            rule['date'] = addRuleWindow.customDatePicker.date.toString('yyyy MM dd')
            if not rule['date']:
                rule['split_char'] = ''  # 如果自定义日期为空，则强制将分隔符置为空
            logging.info(f'日期：{rule["date"]}')

        if addRuleWindow.splitCharComboBox.currentIndex() != 4:
            rule['split_char'] = addRuleWindow.splitCharComboBox.text()
        else:
            rule['split_char'] = addRuleWindow.customSplitCharLineEdit.text()
        logging.info(f'分隔符：{rule["split_char"] if rule["split_char"] else '无'}')

    elif rule['type'] == 5:
        rule['num_type'] = addRuleWindow.numTypeComboBox.currentIndex()
        logging.info(f'编号样式：{rule["num_type"]}')

        if addRuleWindow.fileNameComboBox.currentIndex() == 1:
            rule['new_name'] = addRuleWindow.newNameLineEdit.text()
            logging.info(f'文件名：{rule["new_name"]}')
        elif addRuleWindow.fileNameComboBox.currentIndex() == 0:
            rule['use_original_name'] = True
            logging.info('文件名：原文件名')

        if not addRuleWindow.startNumLineEdit.text():
            rule['start_num'] = 1
        else:
            rule['start_num'] = int(addRuleWindow.startNumLineEdit.text())
        logging.info(f'起始编号：{rule['start_num']}')

        if not addRuleWindow.stepLengthLineEdit.text():
            rule['step_length'] = 1
        else:
            rule['step_length'] = int(addRuleWindow.stepLengthLineEdit.text())
        logging.info(f'步长：{rule['step_length']}')

        if addRuleWindow.posLayout.headBtn.isChecked():
            rule['position'] = 'head'
            logging.info(f'位置：头部')
        elif addRuleWindow.posLayout.tailBtn.isChecked():
            rule['position'] = 'tail'
            logging.info(f'位置：尾部')

    elif rule['type'] == 6:
        rule['action_scope'] = addRuleWindow.actionScopeGroup.checkedId()
        if rule['action_scope'] == 1:
            logging.info('作用域：仅文件名')
        elif rule['action_scope'] == 2:
            logging.info('作用域：仅扩展名')
        elif rule['action_scope'] == 3:
            logging.info('作用域：全部')

        rule['function'] = addRuleWindow.functionGroup.checkedId()
        if rule['function'] == 1:
            logging.info('模式：全部大写')
        elif rule['function'] == 2:
            logging.info('模式：全部小写')
        elif rule['function'] == 3:
            logging.info('模式：首字母大写')

    elif rule['type'] == 7:
        rule['string'] = addRuleWindow.strInputLineEdit.text()
        logging.info(f'自定义字符串：{rule["string"]}')

        if addRuleWindow.posLayout.headBtn.isChecked():
            rule['position'] = 'head'
            logging.info(f'位置：头部')
        elif addRuleWindow.posLayout.tailBtn.isChecked():
            rule['position'] = 'tail'
            logging.info(f'位置：尾部')

    return rule


def import_rule(src_path):
    """
    功能：导入外部规则文件
    参数 src_path：导入的规则文件路径
    返回：导入结果和提示语
    """

    class FileCopyValidator:
        """文件内容验证器"""

        def __init__(self, src_path):
            self.src_path = src_path
            self.dst_path = rule_path

        def safeCopy(self):
            try:
                with open(self.src_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        if content.get('num') is not None and content.get('rules') is not None:
                            shutil.copy(self.src_path, self.dst_path)
                        else:
                            raise ValueError
                    else:
                        raise ValueError
            except JSONDecodeError:
                return False, '不是有效的JSON格式'
            except FileNotFoundError:
                return False, '待导入的文件不存在'
            except ValueError:
                return False, '文件内容格式错误'
            else:
                return True, '文件复制成功'

    validator = FileCopyValidator(src_path)
    return validator.safeCopy()


def export_rule(dst_path):
    """
    功能：导出规则文件到指定位置
    参数 dst_path：导出到的文件夹路径
    返回：导出结果和提示语
    """
    file_name = datetime.now().strftime('%Y_%m_%d_') + 'FC_rule.json'
    try:
        shutil.copy(rule_path, os.path.join(dst_path, file_name))
    except FileNotFoundError:
        return False, '规则文件不存在'
    else:
        return True, '规则导出成功'
