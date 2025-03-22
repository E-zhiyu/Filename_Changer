# file_operations/file_utils.py
import os

"""
文件操作模块
"""


def get_files_in_directory(directory):
    """获取指定目录的所有文件"""
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def rename_files(directory, old_name, new_name):
    """重命名文件"""
    os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
