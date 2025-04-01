# FilenameChanger/log/log_recorder.py
import logging

"""
日志记录模块
"""

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(filename)s/%(levelname)s] : %(message)s',
    filename='./log/app.log',
    filemode='a',
    encoding='utf-8'
)

logger = logging.getLogger(__name__)
