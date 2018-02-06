import sys
import os

if __package__ and "rook" in __package__:
    from rook.lib.config import ConfigManager, ConfigurationScheme
else:
    from lib.config import ConfigManager, ConfigurationScheme

try:
    from .certificates import ROOKOUT_SERVER_CERT
except ImportError:
    # This is caused by not changing sys.path in Rook combined with the way we package the code
    ROOKOUT_SERVER_CERT = None


########################################################################################################################
# General Purpose Configurations
########################################################################################################################


class LoggingConfiguration(ConfigurationScheme):
    LOGGER_NAME = None
    FILE_NAME = None
    LOG_TO_STDERR = True
    LOG_LEVEL = "DEBUG"
    PROPAGATE_LOGS = False
    LOG_TO_REMOTE = False


class VersionConfiguration(ConfigurationScheme):
    VERSION = "No Version Info"
    COMMIT = "No Commit Info"


class CertificatesConfig(ConfigurationScheme):
    # True ( Verify with signed CA) | False (Don't verify) | "path/crt.crt" Use specific certificate
    VERIFY_SERVER_SSL = True


class DefaultConfiguration(ConfigurationScheme):
    DEFAULT_CONFIG_FILE_NAME = "rookout-config.json"
    LOAD_FROM_APP_FOLDER = True
    IGNORE_FILE = None
    USER_CONFIGURATION_FILE = None


class ErrorConfiguration(ConfigurationScheme):
    STACK_DEPTH = 10


class ProtobufConfiguration(ConfigurationScheme):
    NAMESPACE_SERIALIZER_DUMPING = r""


########################################################################################################################
# Rook Configurations
########################################################################################################################


class AgentAddress(ConfigurationScheme):
    HOST = 'localhost'
    PORT = 7486


class AgentComConfiguration(ConfigurationScheme):
    COMMAND_THREAD_NAME = "rookout_agent_com"
    MAX_MESSAGE_LENGTH = 100 * 1024 * 1024
    TOTAL = 2 ** 20
    CONNECT = TOTAL
    READ = 3
    BACK_OFF = 0.2
    MAX_SLEEP = 60
    GRPC_TIMEOUT = 5


class OutputConfiguration(ConfigurationScheme):
    FLUSH_TIME_INTERVAL = 0.25
    THREAD_NAME = "rookout_output_thread"
    MAX_ITEMS = 1000


class InstrumentationConfig(ConfigurationScheme):
    ENGINE = "auto"


class ImportServiceConfig(ConfigurationScheme):
    USE_IMPORT_HOOK = False
    SYS_MODULES_QUERY_INTERVAL = 0.25
    THREAD_NAME = "rookout_import_service_thread"


class LoggingServiceConfig(ConfigurationScheme):
    BASIC_CONFIG_ROOT = True


########################################################################################################################
# Agent Configurations
########################################################################################################################


class ConfigurationFiles(ConfigurationScheme):
    AGENT_IDENTITY = "identity.json"


class RookServerConfiguration(ConfigurationScheme):
    LISTEN_LOCAL = True
    PORT = 7486
    THREADS = 150
    MAX_MESSAGE_LENGTH = 30 * 1024 * 1024
    MAX_RPC_ERRORS = 5


class HttpRetries(ConfigurationScheme):
    TOTAL = 2 ** 20
    CONNECT = TOTAL
    READ = 0
    BACK_OFF = 0.2
    MAX_SLEEP = 120


class RooksManagerConfiguration(ConfigurationScheme):
    MAX_DELAY = 3


class LoginInformation(ConfigurationScheme):
    TOKEN = "7f8c7602f02fcb0d9feaf15bc19adeadbeefb4b32c637d8c4b037b4d558e7bdd"


class ControlServerConfiguration(ConfigurationScheme):
    HOST = "app.rookout.com"
    SECURE = True

    MAX_RETRIES = 1024

    DEFAULT_KEYWORDS = {'org_id': 'rookout'}
    USER = "service"

    THREADS = 4

    SEND_DATA = True

    class WebSocket(ConfigurationScheme):
        URL = "/apiv1/rtm/agents"

    class Rest(ConfigurationScheme):
        pass


class ProcessingConfiguration(ConfigurationScheme):
    RULE_REMOVAL_DELAY = 300
    RULE_DELETION_FREQUENCY = 10
    THREAD_POOL_SIZE = 2


class AgentOutputConfiguration(ConfigurationScheme):
    THREAD_POOL_SIZE = 2
    FLUSH_TIME_INTERVAL = 1
    THREAD_NAME = "agent_output_thread"


class AgentIdentity(ConfigurationScheme):
    ID = None


class MachineIdentity(ConfigurationScheme):
    ID = None


class AgentInfo(ConfigurationScheme):
    TAGS = []


########################################################################################################################
# Backend Configurations
########################################################################################################################


class RookoutServerConfig(ConfigurationScheme):
    # Port server will listen on
    PORT = 443
    # Key used by server to encrypt cookies
    SECRET_KEY = None
    # Admin user default password
    ADMIN_TUPLE = None
    # The name agents used for token based logins
    AGENT_USER_NAME = "service"
    # Service user default password
    SERVICES_USER_TUPLE = None
    # SSL {"certfile": "file.crt", "keyfile": "file.key"} (HTTPS) | None (HTTP instead of HTTPS)
    SSL_OPTIONS = None
    # The REDIS SERVER used for DB "104.197.26.251"  # Internal="10.128.0.3"  or None for localhost
    DB_HOST = None
    # Additional ports the server will listen on and will redirect to chosen port {port: (port, scheme)}
    REDIRECT_PORTS = {}
    # Should the server run in test mode
    TEST_MODE = False
    # Values used to create a test organization
    TEST_ORGANIZATION_INFO = {}
    TEST_USER_INFO = {}


class BackendDbConfig(ConfigurationScheme):
    DB_TYPE = None
    DB_FACTORY = None
    DB_NAME = 'mymaster'


class ExternalServices(ConfigurationScheme):
    class Github(ConfigurationScheme):
        NAME = "github"
        CLIENT_ID = '2b568154dda9127185b2'
        CLIENT_SECRET = None

    class GithubDev(ConfigurationScheme):
        NAME = "github"
        CLIENT_ID = 'd836af82fc21d09169a5'
        CLIENT_SECRET = None

    class GithubStaging(ConfigurationScheme):
        NAME = "github"
        CLIENT_ID = '859d3b32b6babd0be3a9'
        CLIENT_SECRET = None

    class Loggly(ConfigurationScheme):
        NAME = "loggly"
        TOKEN = None


manager = ConfigManager(sys.modules[__name__])


def _load_config_file():
    # Calculate package path
    if 'rook' in __name__:
        # Find the rook directory
        import rook
        package_path = rook.__path__[0]
    elif sys.argv[0].endswith('/rookout-agent.py') or sys.argv[0].endswith('rookout-agent'):
        try:
            import agent
            package_path = agent.__path__[0]
        except ImportError:
            pass
    else:
        package_path = None

    # If a package configuration file exists, load it
    if package_path:
        package_config = os.path.join(package_path, DefaultConfiguration.DEFAULT_CONFIG_FILE_NAME)
        manager.safe_load_json_file(package_config)

    # If a user configuration file exists, load it
    if DefaultConfiguration.USER_CONFIGURATION_FILE:

        # Get full path
        if os.path.isabs(DefaultConfiguration.USER_CONFIGURATION_FILE):
            user_config_path = DefaultConfiguration.USER_CONFIGURATION_FILE
        elif "darwin" in sys.platform:
            user_config_path = os.path.join(os.getenv("HOME"), DefaultConfiguration.USER_CONFIGURATION_FILE)
        elif sys.platform == "win32":
            user_config_path = os.path.join(os.environ['USERPROFILE'], DefaultConfiguration.USER_CONFIGURATION_FILE)
        else:
            user_config_path = os.path.join("/etc", DefaultConfiguration.USER_CONFIGURATION_FILE)

        manager.safe_load_json_file(user_config_path)

    # If an app configuration file exists, load it
    if DefaultConfiguration.LOAD_FROM_APP_FOLDER:
        app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        if app_path == package_path:
            return

        if DefaultConfiguration.IGNORE_FILE and os.path.exists(os.path.join(app_path, DefaultConfiguration.IGNORE_FILE)):
            return

        app_config = os.path.join(app_path, DefaultConfiguration.DEFAULT_CONFIG_FILE_NAME)
        manager.safe_load_json_file(app_config)


_load_config_file()
