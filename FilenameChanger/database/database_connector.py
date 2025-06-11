"""
数据库连接模块
"""
import json

import pymysql.cursors
from cryptography.fernet import Fernet

from FilenameChanger.log.log_recorder import *
from FilenameChanger import database_directory


def decrypt_password(encrypted_password):
    """解密密码"""
    with open(os.path.join(database_directory, 'secret.key'), 'rb') as key_file:
        key = key_file.read()
    f = Fernet(key)
    return f.decrypt(encrypted_password).decode()


def loadConnectionInfos():
    """读取文件中的连接参数"""
    try:
        with open(os.path.join(database_directory, 'password.dat'), 'rb') as password_file:
            b_password = password_file.read()
            password = decrypt_password(b_password)  # 解密密码
    except FileNotFoundError:
        logging.warning('密钥文件或密码文件丢失，密码自动填充为空')
        password = ''  # 密码文件或密钥文件丢失则默认为空

    try:
        with open(os.path.join(database_directory, 'connection.json'), 'r') as connection_file:
            connection = json.load(connection_file)
        host = connection['host']
        port = connection['port']
        user = connection['user']
        database = connection['database']
    except FileNotFoundError:
        logging.warning('数据库连接参数文件丢失，各参数已自动填充为空值')
        host = ''
        port = ''
        user = ''
        database = ''

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
    返回：数据库连接、连接情况和提示信息
    """
    connection_infos = loadConnectionInfos()
    host = connection_infos['host']
    port = connection_infos['port']
    user = connection_infos['user']
    database = connection_infos['database']
    password = connection_infos['password']

    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database,
            charset='utf8'
        )
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        if error_code == 2003:
            message = '目标主机的数据库服务未运行'
        elif error_code == 1045:
            message = '用户名或密码错误'
        elif error_code == 1049:
            message = '目标数据库不存在'
        else:
            message = '连接至数据库时出错'
        return None, False, message

    return connection, True, '数据库连接成功'
