"""
数据库连接参数记录模块
"""
import os, json

from FilenameChanger import database_directory
from cryptography.fernet import Fernet


def encrypt_password(password):
    """加密密码"""
    with open(os.path.join(database_directory, 'secret.key'), 'rb') as key_file:
        key = key_file.read()
    f = Fernet(key)
    return f.encrypt(password.encode())


def saveConnectionInfos(connection: dict):
    """将连接参数写入文件"""

    # 若没有密钥文件则生成新密钥
    if not os.path.isfile(os.path.join(database_directory, 'secret_key.key')):
        key = Fernet.generate_key()
        if not os.path.isdir(database_directory):
            os.mkdir(database_directory)
        with open(os.path.join(database_directory, 'secret.key'), 'wb') as f:
            f.write(key)

    # 将传入的字典内容保存至文件
    password = connection['password']
    safe_password = encrypt_password(password)
    with open(os.path.join(database_directory, 'password.dat'), 'wb') as f:
        f.write(safe_password)

    new_dict = connection
    del new_dict['password']
    with open(os.path.join(database_directory, 'connection.json'), 'w', encoding='utf8') as f:
        json.dump(new_dict, f, indent=4)
