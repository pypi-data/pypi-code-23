import os
import logging
import socket
import re
from enum import EnumMeta

import click
import errbot_rethinkdb_storage

import anji_core.backends as anji_core_backends
from ..types import NodeType, SecurityModel

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['AnjiConfig', 'EnumType']


class AnjiConfig:  # pylint: disable=too-many-instance-attributes,too-few-public-methods

    def __init__(self, node_type: NodeType, bot_name: str) -> None:
        # Storage configuration
        self.BOT_EXTRA_STORAGE_PLUGINS_DIR = errbot_rethinkdb_storage.__path__[0]
        self.STORAGE = 'RethinkDB'
        # Base backend configuration
        self.BACKEND = os.environ.get('ERRBOT_BACKEND')
        self.BOT_EXTRA_BACKEND_DIR = anji_core_backends.__path__[0]
        self.BOT_LOG_LEVEL = logging.INFO
        self.BOT_LOG_FILE = None
        if node_type != NodeType.master:
            self.BOT_ASYNC = False
        self.BOT_DATA_DIR = './data'
        self.BOT_EXTRA_PLUGIN_DIR = None
        self.BOT_IDENTITY = {
            'token': os.environ.get('ERRBOT_TOKEN'),
        }
        if self.BACKEND == 'Telegram':
            self.BOT_ADMINS = (int(os.environ.get('ERRBOT_ADMIN_NICKNAME')),)
        else:
            self.BOT_ADMINS = (os.environ.get('ERRBOT_ADMIN_NICKNAME'),)
        self.BOT_PREFIX = os.environ.get('ERRBOT_PREFIX', '!')
        self.BOT_ALT_PREFIXES = (os.environ.get('ANJI_ALT_PREFIXES', '@anji-tan'),)
        self.DIVERT_TO_THREAD = ('help', 'about')
        # Sentry configuration
        self.SENTRY_DSN = os.environ.get('ERRBOT_SENTRY_DNS', '')
        self.BOT_LOG_SENTRY = bool(self.SENTRY_DSN)
        self.SENTRY_LOGLEVEL = getattr(logging, os.environ.get('ERRBOT_SENTRY_LOG_LEVEL', 'ERROR'))
        # Anji configuration
        self.ANJI_EXTERNAL_MODULES = os.environ.get('ANJI_EXTERNAL_MODULES', '')
        # Bot commands configuration
        self.CONFIRM_DURATION = int(os.environ.get('CONFIRM_DURATION', '30'))
        self.ANJI_HEALTHY_CHECK_TIMEOUT = int(os.environ.get('ANJI_HEALTHY_CHECK_TIMEOUT', '30'))
        # Bot env configuration
        self.ANJI_BOT_TYPE = node_type
        self.ANJI_BOT_NAME = bot_name
        self.ANJI_HOSTNAME = os.environ.get('ANJI_HOSTNAME', socket.gethostname())
        # Consul configuration
        self.ANJI_CONSUL_AGENT_HOST = os.environ.get('ANJI_CONSUL_AGENT_HOST', '127.0.0.1')
        self.ANJI_CONSUL_AGENT_PORT = os.environ.get('ANJI_CONSUL_AGENT_PORT', '8500')
        self.ANJI_CONSUL_AGENT_SCHEME = os.environ.get('ANJI_CONSUL_AGENT_SCHEME', 'http')
        # RethinkDB Configuration
        self.ANJI_RETHINK_DB_HOST = os.environ.get('ANJI_RETHINK_DB_HOST', '127.0.0.1')
        self.ANJI_RETHINK_DB_PORT = int(os.environ.get('ANJI_RETHINK_DB_PORT', '28015'))
        self.ANJI_RETHINK_DB_USER = os.environ.get('ANJI_RETHINK_DB_USER', 'admin')
        self.ANJI_RETHINK_DB_PASSWORD = os.environ.get('ANJI_RETHINK_DB_PASSWORD', '')
        self.ANJI_RETHINK_DB = os.environ.get('ANJI_RETHINK_DB', 'queue_test')
        self.ANJI_CUTOFF_COEF = float(os.environ.get('ANJI_CUTOFF_COEF', 0.2))
        self.ANJI_GLOBAL_SECURITY_MODEL = os.environ.get('ANJI_GLOBAL_SECURITY_MODEL', SecurityModel.free_for_anyone)

        if self.ANJI_BOT_TYPE in [NodeType.cron_worker, NodeType.worker, NodeType.system_analyze]:
            self.CORE_PLUGINS = ()
        elif self.ANJI_BOT_TYPE == NodeType.master:
            self.CORE_PLUGINS = ('Utils')

        self.STORAGE_CONFIG = {
            'host': self.ANJI_RETHINK_DB_HOST,
            'port': self.ANJI_RETHINK_DB_PORT,
            'db': self.ANJI_RETHINK_DB,
            'user': self.ANJI_RETHINK_DB_USER,
            'password': self.ANJI_RETHINK_DB_PASSWORD
        }

    def __str__(self) -> str:
        return "\n".join((f"{key}={value}" for key, value in self.__dict__.items()))


class EnumType(click.Choice):

    def __init__(self, enum, casesensitive=True):
        if isinstance(enum, tuple):
            choices = (_.name for _ in enum)
        elif isinstance(enum, EnumMeta):
            choices = enum.__members__
        else:
            raise TypeError("`enum` must be `tuple` or `Enum`")

        if not casesensitive:
            choices = (_.lower() for _ in choices)

        self._enum = enum
        self._casesensitive = casesensitive
        super().__init__(list(sorted(set(choices))))

    def convert(self, value, param, ctx):
        if not self._casesensitive:
            value = value.lower()

        value = super().convert(value, param, ctx)

        if not self._casesensitive:
            return next(_ for _ in self._enum if _.name.lower() == value.lower())
        return next(_ for _ in self._enum if _.name == value)

    def get_metavar(self, param):
        word = self._enum.__name__

        word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', word)
        word = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', word)
        word = word.replace("-", "_").lower().split("_")

        if word[-1] == "enum":
            word.pop()

        return ("_".join(word)).upper()
