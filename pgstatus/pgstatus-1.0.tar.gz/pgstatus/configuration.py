
import os
import configobj


DEFAULT_CONFIG_PATH = '~/.config/pgstatus.conf'

DEFAULT_CONFIGURATION = {
    'httpd': {
        'port': 5433,
    },
    'connection': {
        'dbname': 'postgres',
        'connect_timeout': 5,
    },
}

class ConfigurationError(Exception):
    pass


class Configuration(dict):
    """
    Configuration file parser for pgstatus.

    Arguments to psycopg2.connect can be specified in 'connection' section of pgstatus.conf,
    see http://initd.org/psycopg/docs/module.html#psycopg2.connect

    Do not configure async or cursor_factory pararmeters, these will break the tests
    """

    def __init__(self, dbname=None, path=DEFAULT_CONFIG_PATH):

        self.update(**DEFAULT_CONFIGURATION)
        if dbname is not None:
            self['connection']['dbname'] = dbname

        filename = os.path.expandvars(os.path.expanduser(path))
        if not os.path.isfile(filename):
            raise ConfigurationError('No such file: {0}'.format(path))
        if not os.access(filename, os.R_OK):
            raise ConfigurationError('Permission denind: {0}'.format(path))

        try:
            data = configobj.ConfigObj(filename)
            for key, value in data.get('connection', {}).items():
                self['connection'][key] = value
            for key, value in data.get('httpd', {}).items():
                self['httpd'][key] = value
        except Exception as e:
            raise ConfigurationError('Invalid configuration file {0}: {1}'.format(path, e))

        if 'dbname' not in self['connection']:
            raise ConfigurationError('Database to monitor not specified in configuration.')

        self['httpd']['port'] = int(self['httpd']['port'])
