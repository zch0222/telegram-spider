import logging
from logging.handlers import RotatingFileHandler


def get_logger():
    logger = logging.getLogger("my_logger")
    return logger
