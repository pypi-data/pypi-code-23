import logging
import os
import warnings

import yaml
from distutils.version import LooseVersion

from .rest import RESTClientObject, DataRobotClientConfig
from ._version import __version__
from .errors import ClientError


logger = logging.getLogger(__package__)

__all__ = ('Client', 'get_client', 'set_client')

_global_client = None


def Client(token=None, endpoint=None, config_path=None, connect_timeout=None,
           user_agent_suffix=None, ssl_verify=True):
    """Return global `RESTClientObject` with optional configuration.
    Missing configuration will be read from env or config file.

    Parameters
    ----------
    token : str, optional
        API token
    endpoint : str, optional
        Base url of API
    config_path : str, optional
        Alternate location of config file
    connect_timeout : float, optional
        How long the client should be willing to wait before establishing a connection with
        the server
    user_agent_suffix : str, optional
        Additional text that is appended to the User-Agent HTTP header when communicating with
        the DataRobot REST API. This can be useful for identifying different applications that
        are built on top of the DataRobot Python Client, which can aid debugging and help track
        usage.
    ssl_verify : bool or str, optional
        Whether to check SSL certificate.
        Could be set to path with certificates of trusted certification authorities
    """
    global _global_client
    env_config = _get_config_file_from_env()
    if token and endpoint:
        drconfig = DataRobotClientConfig(endpoint=endpoint, token=token,
                                         connect_timeout=connect_timeout,
                                         user_agent_suffix=user_agent_suffix,
                                         ssl_verify=ssl_verify)
    elif config_path:
        if not _file_exists(config_path):
            raise ValueError('Invalid config path - no file at {}'.format(config_path))
        drconfig = _config_from_file(config_path)
    elif env_config:
        if not _file_exists(env_config):
            raise ValueError('Invalid config path - no file at {}'.format(env_config))
        drconfig = _config_from_file(env_config)
    else:
        try:
            drconfig = _config_from_env()
        except ValueError:
            default_config_path = _get_default_config_file()
            if default_config_path is not None:
                drconfig = _config_from_file(default_config_path)
            else:
                raise ValueError('No valid configuration found')
    _global_client = RESTClientObject.from_config(drconfig)
    return _global_client


def _version_warning(client):
    """
    Check that this client version is not ahead of the DataRobot version that
    the server points to. There will be unsupported functionality

    Parameters
    ----------
    client : RESTClientObject
    """
    server_version_string = _get_server_version(client)
    if server_version_string is None:
        return
    server_version = LooseVersion(vstring=server_version_string)
    client_version = LooseVersion(vstring=_get_client_version())
    if server_version.version[0] != client_version.version[0]:
        err_msg = ('Client and server versions incompatible. Server version: {} - '
                   'client version: {}').format(server_version.vstring,
                                                client_version.vstring)
        raise RuntimeError(err_msg)
    if server_version.version[1] < client_version.version[1]:
        warn_msg = 'Client version is ahead of server version, you may have incompatibilities'
        warnings.warn(warn_msg)


def _get_server_version(client):
    try:
        version_info = client.get('version/').json()
        return version_info['versionString']
    except ClientError:
        w_msg_tmpl = ('Server did not reply with an API version. This may indicate the endpoint {} '
                      'is misconfigured, or that the server API version precedes this version '
                      'of the DataRobot client package and is likely incompatible.')
        warnings.warn(w_msg_tmpl.format(client.endpoint))


def _get_client_version():
    return __version__


def get_client():
    if _global_client is None:
        c = Client()
        _version_warning(c)
    return _global_client


class staticproperty(property):
    def __get__(self, instance, owner):
        return self.fget()


def set_client(client):
    """
    Set the global HTTP client for sdk.
    Returns previous client.
    """
    global _global_client
    previous = _global_client
    _global_client = client
    return previous


def _get_config_file_from_env():
    if 'DATAROBOT_CONFIG_FILE' in os.environ:
        config_path = os.environ['DATAROBOT_CONFIG_FILE']
        if os.path.exists(config_path):
            return config_path
        else:
            raise ValueError('Environment variable DATAROBOT_CONFIG_FILE points to a missing file')
    return None


def _get_config_dir():
    return os.path.expanduser('~/.config/datarobot')


def _get_default_config_file():
    first_choice_config_path = os.path.join(_get_config_dir(), 'drconfig.yaml')
    if _file_exists(first_choice_config_path):
        return first_choice_config_path
    else:
        return None


_file_exists = os.path.isfile


def _config_from_env():
    """
    Create and return a DataRobotClientConfig from environment variables.

    There are two ways this can be used:
    1. Use the environment variable DATAROBOT_CONFIG_FILE to specify the path to a yaml config
       file specifying the configuration to use
    2. Use both the environment variables DATAROBOT_ENDPOINT and DATAROBOT_API_TOKEN to specify
       the connection parameters. Note that this method only allows for configuration of endpoint,
       token and user_agent_suffix; any more advanced configuration must be done through a yaml
       file

    Returns
    -------
    config : DataRobotClientConfig

    Raises
    ------
    ValueError
        If either of DATAROBOT_ENDPOINT or DATAROBOT_API_TOKEN is not specified as an environment
        variable
    IOError
        If the config file that DATAROBOT_CONFIG_FILE points to does not exist
    """
    endpoint = os.environ.get('DATAROBOT_ENDPOINT')
    token = os.environ.get('DATAROBOT_API_TOKEN')
    user_agent_suffix = os.environ.get('DATAROBOT_USER_AGENT_SUFFIX')
    if endpoint is None or token is None:
        e_msg = ('Incomplete DataRobot configuration specified in environment variables; both'
                 'DATAROBOT_ENDPOINT and DATAROBOT_API_TOKEN must be specified')
        raise ValueError(e_msg)
    return DataRobotClientConfig(endpoint=endpoint, token=token,
                                 user_agent_suffix=user_agent_suffix)


def _config_from_file(config_path):
    """
    Create and return a DataRobotClientConfig from a config path. The file must be
    a yaml formatted file

    Parameters
    ----------
    config_path : str
        Path to the configuration file

    Returns
    -------
    config : DataRobotClientConfig
    """
    with open(config_path, 'rb') as f:
        data = yaml.load(f)
    return DataRobotClientConfig.from_data(data)
