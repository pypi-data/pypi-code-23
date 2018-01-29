import logging

logger = logging.getLogger('FastGets')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

fomatter = logging.Formatter('[%(asctime)s][%(levelname)s][Thread:%(threadName)s] %(message)s')
ch.setFormatter(fomatter)
logger.addHandler(ch)

logger.level = logging.DEBUG
