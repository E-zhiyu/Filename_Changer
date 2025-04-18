# rename_rules/rule_manager.py
import json
import os
import time

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
            return json.load(f)
    except FileNotFoundError:
        logging.info('未找到配置文件，正在创建并初始化……')
        init_json()
        with open(config_path, 'r', encoding='utf-8') as f:
            logging.info('规则配置已初始化并成功加载')
            return json.load(f)


def save_new_rule(config_dict, new_rule):
    """
    功能：将新规则并入已存在的规则列表
    参数 config_dict：规则配置文件根字典
    参数 new_rule：新规则字典
    参数 config_path：规则文件路径
    """
    config_dict['num'] += 1
    config_dict['rules'].append(new_rule)  # 将新规则字典并入现有的规则

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=4)
    print('新规则已成功保存！')
    logging.info('新规则保存成功')


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


def del_rules(config_dict):
    """
    功能：删除指定的规则
    参数 config_dict：规则配置文件根字典
    """
    if config_dict['num'] == 1:
        logging.error('无法移除最后一个规则')
        print('无法删除最后一个规则！')
        time.sleep(0.5)
        return
    else:
        while True:
            try:
                option = int(input('\n请选择（输入-1取消操作）：\n'))
                if option == -1:
                    logging.info('用户取消删除规则')
                    print('已取消，正在返回主菜单……')
                    time.sleep(0.5)
                    return  # 结束函数跳出死循环
                elif option <= 0 or option > config_dict['num']:  # 确保输入有效值
                    raise ValueError
                else:
                    logging.info(f'用户删除第{option}个规则')

                    # 判断删除的规则是否被选中，删除被选中的规则则改为选中第一个规则
                    if config_dict['selected_index'] == option - 1 and option != 1:  # 当删除第一个规则时仍然默认选中规则1
                        logging.info(f'第{option}个规则为选中的规则，已更改至删除后的第一个规则')
                        print(f'第{option}个规则是选中的规则，已更改至第一个规则！')
                        config_dict['selected_index'] = 0

                    # 若删除的规则下标小于选中的规则，则将selected_index-1
                    if option - 1 < config_dict['selected_index']:
                        config_dict['selected_index'] -= 1

                    config_dict['num'] -= 1
                    del config_dict['rules'][option - 1]
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_dict, f, ensure_ascii=False, indent=4)
                    print(f'规则{option}已删除！')
                    time.sleep(0.5)
                    return  # 结束函数跳出死循环
            except ValueError:
                print('请选择一个有效的规则！')


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
