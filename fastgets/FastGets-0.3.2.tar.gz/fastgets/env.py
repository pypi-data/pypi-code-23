# coding: utf8


TEST = 'test'
LOCAL = 'local'
DISTRIBUTED = 'distributed'
WORK = 'work'
API = 'api'
SCRIPT = 'script'

mode = None
instance_id = None

configured = False

REDIS_CONFIG, MONGO_CONFIG, API_CONFIG, PROJECT_ROOT_DIR, TEMPLATES_DIR, SCRIPTS_DIR, COOKIES_DIR = [None] * 7


FASTGETS_DIR = __file__.split('fastgets')[0]
