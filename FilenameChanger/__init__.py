import os.path

python_version = '3.13'

version = "1.2.0"
author = 'GitHub@E-zhiyu'
config_path = './rename_rules/rename_rules.json'  # 重命名规则文件路径

# 程序运行时判断是否存在log文件夹
if not os.path.isdir('./log'):
    os.mkdir('./log')
