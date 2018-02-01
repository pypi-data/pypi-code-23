################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################
import sys
import getopt
import logging


def get_logger(name, specific_log_level=None):
    default_log_level = logging.WARN

    optlist, args = getopt.getopt(sys.argv[2:], ':', ['log='])
    try:
        env_log_level = getattr(logging, [x for x in optlist if x[0] == "--log"][0][1], None)
    except:
        env_log_level = None

    log_level = default_log_level

    if env_log_level is not None:
        log_level = env_log_level

    if specific_log_level is not None:
        log_level = specific_log_level

    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % log_level)

    logger = logging.getLogger(name)
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.setLevel(log_level)
    # logger.info('Set logger level: {}'.format(logging.getLevelName(log_level)))
    return logger
