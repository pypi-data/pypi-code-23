# -*- coding: utf-8 -*-

import ast
import configparser as config_parser
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__all__ = ['get_option', 'get_section', 'get_sections', 'get_config', 'get_env', 'get_config_files_detected',
           'set_config_dir']


def _literal_eval(val):
    try:
        return ast.literal_eval(val)
    except (SyntaxError, ValueError):
        return val


class _Interpolation:
    """Interpolation class to parse/modify option values"""

    def before_get(self, parser, section, option, value, defaults):
        return _literal_eval(value)

    def before_set(self, parser, section, option, value):
        return _literal_eval(value)

    def before_read(self, parser, section, option, value):
        return value

    def before_write(self, parser, section, option, value):
        return value


_config = config_parser.ConfigParser(interpolation=_Interpolation())
_config.optionxform = str
_sections = {}
_env = None
_config_dir = None
_config_files_detected = []


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
    """
    Detects environment
    """
    global _env
    if os.environ.get('__ENV__', None) is not None:
        _env = os.environ.get('__ENV__').lower()


def get_env():
    """
    Getter for _env
    """
    return _env


def set_config_dir(d):
    """
    Setter for _config_dir
    """
    global _config_dir, _config_files_detected, _sections

    _config_dir = d

    _config_files_detected = []
    _sections = {}

    _read_file_config_main()
    _read_file_config_env()
    _read_env()


def get_config_dir():
    """
    Getter for _config_dir
    """
    return _config_dir


def get_config_files_detected():
    """
    Getter for _config_files_detected
    """
    return _config_files_detected


def _gen_lookup_dirs():
    """
    Generates directories to search configuration files
    """

    # If _config_dir specified by user, only searches in that dir
    if _config_dir is not None:
        dirs = [_config_dir]
    else:
        # Caller script's dir
        dirs = [os.path.abspath(os.getcwd())]

        # Caller script's parent dir
        dirs += [os.path.abspath(os.path.join(os.getcwd(), '..'))]

        # Caller script's 2. parent dir
        dirs += [os.path.abspath(os.path.join(os.getcwd(), '..', '..'))]

    return dirs


def _read_file_config_main():
    """
    Reads options from default config file config.ini
    Config.ini should contain the most basic configuration file
    """
    global _config_files_detected, _sections

    file_list = [os.path.join(x, 'config.ini') for x in _gen_lookup_dirs()]

    config_flag = False
    for file in file_list:
        if os.path.isfile(file):
            _config.read(file)
            _config_files_detected.append(file)
            _sections = {s: dict(_config.items(s)) for s in _config.sections()}
            config_flag = True
            break

    if not config_flag:
        logger.info('No configuration file found. Looked for: {}'.format(', '.join(file_list)))


def _read_file_config_env():
    """
    Reads options from config file according to detected environment.
    """
    global _config_files_detected, _sections

    if _env is not None and _env.lower() in ['testing', 'production']:
        config_file_name = 'config.{}.ini'.format(_env)
    else:
        config_file_name = 'config.development.ini'

    file_list = [os.path.join(x, config_file_name) for x in _gen_lookup_dirs()]

    for file in file_list:
        if os.path.isfile(file):
            _config.read(file)
            _config_files_detected.append(file)
            _sections = {s: dict(_config.items(s)) for s in _config.sections()}
            break


def _read_env():
    """
    Reads options from environment variables.

    Definition example:

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
    """
    Returns option value by section name and option name
    """
    return _config.get(section, option)


def get_section(section):
    """
    Returns section dictionary by section name
    """
    return _sections[section]


_detect_env()
_read_file_config_main()
_read_file_config_env()
_read_env()
