# FilenameChanger/log/log_recorder.py
import logging

logger = logging.getLogger(__name__)
"""
日志记录模块
"""

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    filename='./log/app.log',
    filemode='a',
    encoding='utf-8'
)
