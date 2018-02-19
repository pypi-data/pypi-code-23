import logging
import os
import shutil
import sys


LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def a_logger(name, level="WARNING", filename=None, mode="a"):
    log_format = '%(asctime)s|%(levelname)-8s|%(name)s |%(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    logger = logging.getLogger(name)
    if not isinstance(level, int):
        try:
            level = getattr(logging, level)
        except AttributeError:
            raise ValueError("unsupported literal log level: %s" % level)
        logger.setLevel(level)
    if filename:
        handler = logging.FileHandler(filename, mode=mode)
    else:
        handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format, datefmt=log_datefmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


# from http://stackoverflow.com/questions/19044096/how-to-import-a-submodule-in-
# python-without-exec
def import_from(mod_name, var_name, error_msg=None):
    import importlib
    var = None
    try:
        mod = importlib.import_module(mod_name)
        var = getattr(mod, var_name)
    except ImportError:
        if not error_msg:
            error_msg = 'Module {} missing'.format(mod_name)

    assert var is not None, error_msg
    return var


# from http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-
# exists-and-create-it-if-necessary/5032238#5032238
def ensure_dir(path, force=False):
    try:
        if force and os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def path_exists(path, force=False):
    def missing(p, f):
        if f:
            print("path - {} - doesn't exists".format(p))
            sys.exit()
        return False

    return True if os.path.exists(os.path.expanduser(path)) else missing(path,
                                                                         force)
