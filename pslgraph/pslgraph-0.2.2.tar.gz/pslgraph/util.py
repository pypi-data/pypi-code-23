import logging

from .constants import *

# Keep track of loggers so we can change their level globally.
_loggers = []

def computeNodeLabel(nodeID, nodeModifier):
    if (nodeModifier != NODE_MODIFIER_SOURCE and nodeModifier != NODE_MODIFIER_TARGET):
        raise ValueError("Node modifier must be NODE_MODIFIER_SOURCE/NODE_MODIFIER_TARGET, found: %s" % (nodeModifier))

    return (int(nodeID) + 1) * nodeModifier

def write_tsv(path, rows):
    with open(path, 'w') as file:
        # TODO(eriq): Batch
        for row in rows:
            file.write("\t".join(row) + "\n")

def get_logger(name):
    if (len(_loggers) == 0):
        logging.basicConfig(level = logging.INFO, format = '%(asctime)s [%(levelname)s] %(name)s -- %(message)s')

    logger = logging.getLogger(__name__)
    _loggers.append(logger)
    return logger

def set_logging_level(level = logging.INFO):
    for logger in _loggers:
        logger.setLevel(level)
