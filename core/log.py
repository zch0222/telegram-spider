import logging
from logging.handlers import RotatingFileHandler


def get_logger():
    logger = logging.getLogger("my_logger")
    formatter = logging.Formatter('%(levelname)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
