import logging.handlers
import os


def logger_config(name, level):
    LOG_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
    LOG_FOLDER_PATH = os.path.join(LOG_FOLDER_PATH, 'log')
    LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, '{}.log'.format(name))
    if not os.path.exists(LOG_FOLDER_PATH):
        os.mkdir(LOG_FOLDER_PATH)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] : %(message)s")
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE_PATH, when='d')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)
