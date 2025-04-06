# FilenameChanger/log/log_recorder.py
import logging
import os
from datetime import datetime

"""
日志记录模块
"""

log_dir = './logs'


class DailyFileHandler(logging.FileHandler):
    def __init__(self, log_dir):
        """
        功能：每天动态生成YYYY-MM-DD.log
        参数 log_dir：日志文件夹路径
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        filename = self.get_today_filename()
        super().__init__(filename, encoding='utf-8')

    def get_today_filename(self):
        """
        功能：生成当前日期对应的文件名
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.log_dir, f'{today}.log')

def setup_logger():
    formatter = logging.Formatter('%(asctime)s - [%(filename)s/%(levelname)s] : %(message)s')
    handler = DailyFileHandler(log_dir)
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

setup_logger()
