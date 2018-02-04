import os
from localstack import config as localstack_config
from localstack import constants as localstack_constants
from localstack.config import HOSTNAME, USE_SSL

# version of localstack-ext
VERSION = '0.8.1'

# api server config
API_PATH = '/v1'
API_PORT_LOCAL = 8183
API_URL = localstack_constants.API_ENDPOINT

# api endpoints
API_PATH_SUBSCRIBE = '%s/subscribe' % API_PATH
API_PATH_ACTIVATE = '%s/activate' % API_PATH
API_PATH_EVENTS = '%s/events' % API_PATH
API_PATH_GITHUB = '%s/github' % API_PATH
API_PATH_USER = '%s/user' % API_PATH
API_PATH_CONFIG = '%s/config' % API_PATH
API_PATH_CI = '%s/ci' % API_PATH

ROOT_FOLDER = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

PROTECTED_FOLDERS = ('services', 'utils')

# database connection settings
DB_NAME = 'localstack'
DB_USER = os.environ.get('DB_USER') or 'localstack'
DB_PASS = os.environ.get('DB_PASS')

# address of local DNS server (the default is a fairly arbitrarily
# chosen IP address that should not clash with local network ranges)
DNS_ADDRESS = os.environ.get('DNS_ADDRESS') or '200.200.55.55'

# add default service ports
localstack_constants.DEFAULT_SERVICE_PORTS['cognito-idp'] = 4590
localstack_constants.DEFAULT_SERVICE_PORTS['cognito-identity'] = 4591
localstack_constants.DEFAULT_SERVICE_PORTS['sts'] = 4592
localstack_constants.DEFAULT_SERVICE_PORTS['iam'] = 4593
localstack_constants.DEFAULT_SERVICE_PORTS['edge'] = 443

# re-initialize configs in localstack
localstack_config.populate_configs()
