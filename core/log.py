import logging
from logging.handlers import RotatingFileHandler


def get_logger():
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.INFO)  # 设置日志级别

    # 创建一个handler，用于写入日志文件
    handler = RotatingFileHandler(filename="app.log", maxBytes=1000000, backupCount=10)
    handler.setLevel(logging.INFO)

    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(handler)
    return logger
