import logging
import sys
import os
import json
from logging.config import dictConfig
import codecs

DEFAULT_CONFIG = 'config.json'

if not os.path.exists(DEFAULT_CONFIG):
	raise RuntimeError('please create config.json file in your project root folder')

syslog_format = ("[%(name)s][env:{logging_env}] %(levelname)s ""[{hostname}  %(process)d] [%(filename)s:%(lineno)d] ""- %(message)s").format(logging_env="", hostname="")
json_file = open(DEFAULT_CONFIG, 'rb')
reader = codecs.getreader('utf-8')
configurator = json.load(reader(json_file))
json_file.close()

logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('socketIO-client').setLevel(logging.ERROR)
logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'standard': {
			'format': '%(asctime)s %(levelname)s %(process)d '
			          '[%(name)s] %(filename)s:%(lineno)d - %(message)s',
		},
		'syslog_format': {'format': syslog_format},
		'raw': {'format': '%(message)s'},
	},
	'handlers': {
		'console': {
			'level': 'INFO',
			'class': 'logging.StreamHandler',
			'formatter': 'standard',
			'stream': sys.stdout,
		},
		'rotate_file': {
			'level': 'DEBUG',
			'formatter': 'standard',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': configurator['log_file'],
			'encoding': 'utf8',
			'maxBytes': 100000,
			'backupCount': 1,
		}
	},
	'loggers': {
		'requests.packages.urllib3.connectionpool': {
			'handlers': [],
			'propagate': False,
			'level': 'INFO',
		},
		'': {
			'handlers': ['console', 'rotate_file'],
			'level': 'DEBUG',
			'propagate': False
		},
	}
}

dictConfig(LOGGING)
