import logging

from .constants import *

# Keep track of loggers so we can change their level globally.
_loggers = {}
_current_log_level = logging.INFO

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
        logging.basicConfig(
                level = _current_log_level,
                format = '%(asctime)s [%(levelname)s] %(name)s -- %(message)s')

    if (name in _loggers):
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(_current_log_level)

    _loggers[name] = logger
    return logger

def set_logging_level(level = logging.INFO):
    _current_log_level = level
    for name in _loggers:
        _loggers[name].setLevel(level)
