import os
import sys

from python_agent.packages import requests
from python_agent.packages.requests.packages.urllib3.exceptions import InsecureRequestWarning

if sys.version_info < (2, 7):
    from python_agent.packages.dictconfig import dictConfig
else:
    from logging.config import dictConfig

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

__version__ = "0.2.85"
__package_name__ = "sealights-python-agent"


LOG_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sealights-standard': {
            'format': '%(asctime)s %(levelname)s [%(process)d|%(thread)d] %(name)s: %(message)s'
        },
        'standard': {
            'format': '%(asctime)s %(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'cli': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'sealights-console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG' if os.environ.get("SL_DEBUG") else 'INFO',
            'formatter': 'sealights-standard',
            'stream': 'ext://sys.stdout',
        },
        'sealights-file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG' if os.environ.get("SL_DEBUG") else 'INFO',
            'formatter': 'sealights-standard',
            'filename': 'sealights-python-agent.log',
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 10,
        }
    },
    'loggers': {
        'python_agent': {
            'handlers': ['sealights-console'] if os.environ.get("SL_DEBUG") else [],
            'level': 'DEBUG' if os.environ.get("SL_DEBUG") else 'INFO',
            'propagate': False
        },
        '__main__': {
            'handlers': ['cli'],
            'level': 'DEBUG',
            'propagate': True
        },
        'python_agent.build_scanner.executors': {
            'handlers': ['cli'],
            'level': 'DEBUG',
            'propagate': True
        },
        'python_agent.test_listener.executors': {
            'handlers': ['cli'],
            'level': 'DEBUG',
            'propagate': True
        },
        'python_agent.common.token': {
            'handlers': ['cli'],
            'level': 'DEBUG',
            'propagate': True
        },
        'python_agent.admin': {
            'handlers': ['cli'],
            'level': 'DEBUG',
            'propagate': True
        },
        'python_agent.common.configuration_manager': {
            'handlers': ['cli'],
            'level': 'DEBUG',
            'propagate': True
        },
        'python_agent.common.environment_variables_resolver': {
            'handlers': ['cli'],
            'level': 'DEBUG',
            'propagate': True
        },
        'python_agent.packages.requests.packages.urllib3.connectionpool': {
            'handlers': [],
            'level': 'WARN',
            'propagate': False
        },
        'apscheduler': {
            'handlers': [],
            'level': 'CRITICAL',
            'propagate': False
        },
        'pip': {
            'handlers': [],
            'level': 'WARN',
            'propagate': False
        }
    }
}
dictConfig(LOG_CONF)
