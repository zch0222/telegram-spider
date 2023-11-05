import logging
from logging.handlers import RotatingFileHandler


def get_logger():
    logger = logging.getLogger("my_logger")
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
