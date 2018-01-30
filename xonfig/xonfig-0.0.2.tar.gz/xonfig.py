# -*- coding: utf-8 -*-

import ast
import configparser as config_parser
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__all__ = ['get_option', 'get_section', 'get_sections', 'get_config', 'get_env', 'get_config_file_detected',
           'set_config_dir', 'refresh', 'read_env']


def _literal_eval(val):
    try:
        return ast.literal_eval(val)
    except (SyntaxError, ValueError):
        return val


class Interpolation:
    """Interpolation class to parse/modify option values"""

    def before_get(self, parser, section, option, value, defaults):
        return _literal_eval(value)

    def before_set(self, parser, section, option, value):
        return _literal_eval(value)

    def before_read(self, parser, section, option, value):
        return value

    def before_write(self, parser, section, option, value):
        return value


_config = None
_sections = None
_env = None
_config_dir = None
_config_file_detected = None


def init():
    global _config, _sections, _env, _config_dir, _config_file_detected

    _config = config_parser.ConfigParser(interpolation=Interpolation())
    _config.optionxform = str
    _sections = {}
    _env = None
    _config_dir = None
    _config_file_detected = None

    _detect_env()
    _read_file_config()
    read_env()


def refresh():
    """
    An alias for init()
    """
    init()


def get_config():
    """
    Getter for _config object
    """
    return _config


def get_sections():
    """
    Getter for _sections dictionary
    """
    return _sections


def _detect_env():
    global _env
    if os.environ.get('__ENV__', None) is not None:
        _env = os.environ.get('__ENV__')


def get_env():
    """
    Getter for _env
    """
    return _env


def set_config_dir(d):
    """
    Setter for _config_dir
    """
    global _config_dir

    _config_dir = d

    _read_file_config()


def get_config_dir():
    return _config_dir


def get_config_file_detected():
    """
    Getter for _config_file_detected
    """
    return _config_file_detected


def _gen_lookup_dirs():
    # Add some probaly paths

    # Script's dir
    dirs = [os.path.abspath(os.getcwd())]

    # Script's parent dir
    dirs += [os.path.abspath(os.path.join(os.getcwd(), '..'))]

    # Script's 2.parent dir
    dirs += [os.path.abspath(os.path.join(os.getcwd(), '..', '..'))]

    # If _config_dir specified by users, add it to beginning of list
    if _config_dir is not None:
        dirs = [_config_dir] + dirs

    return dirs


def _read_file_config():
    global _config_file_detected, _sections

    if _env is not None:
        config_file_name = 'config.{}.ini'.format(_env.lower())
    else:
        config_file_name = 'config.ini'

    file_list = [os.path.join(x, config_file_name) for x in _gen_lookup_dirs()]

    config_flag = False
    for file in file_list:
        if os.path.isfile(file):
            _config.read(file)
            _config_file_detected = file
            _sections = {s: dict(_config.items(s)) for s in _config.sections()}
            config_flag = True
            break

    if not config_flag:
        _config_file_detected = None
        _sections = {}

        # logger.info('No configuration file found. Looked for: {}'.format(', '.join(file_list)))


def read_env():
    """
    Environment variable definition example:

    __ENV__APP_SQLALCHEMY_DATABASE_URI =>  [__ENV__]   [APP]   [SQLALCHEMY_DATABASE_URI]
                                               ↓         ↓                ↓
                                            Prefix    Section          Option
    """

    global _sections

    config_changed = False

    for key, value in os.environ.items():
        if key.startswith('__ENV__'):
            if len(key.replace('__ENV__', '')) == 0:
                continue

            try:
                section, option = key.replace('__ENV__', '').split('_', 1)
            except ValueError:
                continue

            if not _config.has_section(section):
                _config.add_section(section)

            _config.set(section, option, value)
            config_changed = True

    if config_changed:
        _sections = {s: dict(_config.items(s)) for s in _config.sections()}


def get_option(section, option):
    return _config.get(section, option)


def get_section(section):
    return _sections[section]


init()
