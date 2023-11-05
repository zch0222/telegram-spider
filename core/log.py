import logging
from logging.handlers import RotatingFileHandler


def get_logger():
    logger = logging.getLogger("my_logger")
    formatter = logging.Formatter('%(levelname)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = RotatingFileHandler(filename="app.log", maxBytes=1000000, backupCount=10)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
