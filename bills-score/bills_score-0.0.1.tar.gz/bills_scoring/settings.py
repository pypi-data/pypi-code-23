import os

# CBCI Settings
CBCI_SERVER = {
        "URL": os.getenv("CBCI_URL", "http://192.168.8.152:8000"),
        "USERNAME": os.getenv("CBCI_USERNAME", "admin"),
        "SECRET": os.getenv("CBCI_SECRET", "password123"),
}

FILE_FOLDER_NAME = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'dat')

DATA_FILES_DICT = {
    'DISTRIBUTION_Q': os.path.join(
                        FILE_FOLDER_NAME,
                        'dist_Q.csv'),
    'DISTRIBUTION_M': os.path.join(
                        FILE_FOLDER_NAME,
                        'dist_M.csv'),
}

LOCAL_HTTPD_PORT = os.getenv("BLACKBOX_PORT", "5000")
DB_NAME = os.getenv("DB_NAME", "hola.db")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s -[%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
