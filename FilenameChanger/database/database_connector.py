"""
数据库连接模块
"""
import os, json
import pymysql.cursors
from cryptography.fernet import Fernet

from FilenameChanger import database_directory


def decrypt_password(encrypted_password):
    """解密密码"""
    with open(os.path.join(database_directory, 'secret.key'), 'rb') as key_file:
        key = key_file.read()
    f = Fernet(key)
    return f.decrypt(encrypted_password).decode()


def loadConnectionInfos():
    """读取文件中的连接参数"""
    with open(os.path.join(database_directory, 'password.dat'), 'rb') as password_file:
        b_password = password_file.read()
    password = decrypt_password(b_password)  # 解密密码

    with open(os.path.join(database_directory, 'connection.json'), 'r') as connection_file:
        connection = json.load(connection_file)
    host = connection['host']
    port = connection['port']
    user = connection['user']
    database = connection['database']

    dictionary = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database,
    }

    return dictionary


def create_connection():
    """
    功能：创建数据库连接
    返回：数据库连接
    """
    connection_infos = loadConnectionInfos()
    host = connection_infos['host']
    port = connection_infos['port']
    user = connection_infos['user']
    database = connection_infos['database']
    password = connection_infos['password']

    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=database,
        charset='utf8'
    )

    return connection
