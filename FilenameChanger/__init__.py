import os.path

# 程序运行时判断是否存在log文件夹
if not os.path.isdir('./log'):
    os.mkdir('./log')
