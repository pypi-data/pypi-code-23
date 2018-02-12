"""
Summary:
    keyup Project-level Defaults and Settings

    NOTE: local defaults for your specific installation are derived from
          settings found in ~/.config/keyup/config.ini

Module Attributes:
    - user_home (TYPE str):
        $HOME environment variable, present for most Unix and Unix-like POSIX systems
    - config_dir (TYPE str):
        directory name default for stsaval config files (.stsaval)
    - config_path (TYPE str):
        default for stsaval config files, includes config_dir (~/.stsaval)
    - key_deprecation (TYPE str):
        Deprecation logic that keyup uses when 2 keys exist for a user.

        2 values possible:

            - 'AGE':  keyup deprecates based on age, replacing the oldest key
            - 'AWSCLI':  keyup replaces keys currently in the local awscli config
"""

import os
import inspect
import logging
from keyup.script_utils import read_local_config, get_os
from keyup import __version__

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


# --  project-level DEFAULTS  ------------------------------------------------

try:

    env_info = get_os(detailed=True)
    OS = env_info['os_type']
    user_home = env_info['HOME']

except KeyError as e:
    logger.critical(
        '%s: %s variable is required and not found in the environment' %
        (inspect.stack()[0][3], str(e)))
    raise e
else:
    # local vars -- this section executes as default; if windows, execute diff
    # section with appropriate pathnames

    # project
    PACKAGE = 'keyup'
    version = __version__

    # config parameters
    CONFIG_SCRIPT = 'keyconfig'         # console script to access config file
    config_dir = '.config'
    config_subdir = PACKAGE
    config_filename = 'config.json'
    config_path = user_home + '/' + config_dir + '/' + config_subdir + '/' + config_filename

    # access key parameters
    keyage_min = 1      # days
    keyage_max = 30     # days
    key_deprecation = 'AGE'       # 'AWSCLI' || 'AGE'

    # logging parameters
    enable_logging = False
    log_dir = user_home + '/' + 'logs'
    log_filename = 'keyup.log'
    log_path = log_dir + '/' + log_filename
    log_mode = 'FILE'

    # key backup parameters
    backup_enable = False
    backup_location = user_home + '/' + 'Backup' + '/' + PACKAGE

    seed_config = {
            "PROJECT": {
                "PACKAGE": PACKAGE,
                "CONFIG_VERSION": version,
                "CONFIG_DATE": "",
                "HOME": user_home,
                "CONFIG_FILENAME": config_filename,
                "CONFIG_DIR": config_dir,
                "CONFIG_SUBDIR": config_subdir,
                "CONFIG_PATH": config_path
            },
            "TEMP_CREDENTIALS": {
                "PROFILE_NAMES": []
            },
            "LOGGING": {
                "ENABLE_LOGGING": enable_logging,
                "LOG_FILENAME": log_filename,
                "LOG_PATH": log_path,
                "LOG_MODE": log_mode
            },
            "KEY_METADATA": {
                "KEYAGE_MAX_DAYS": keyage_max,
                "KEYAGE_MIN_DAYS": keyage_min,
                "KEY_DEPRECATION": key_deprecation
            },
            "KEY_BACKUP": {
                "BACKUP_ENABLE": backup_enable,
                "BACKUP_LOCATION": backup_location
            }
        }

try:
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
        os.chmod(log_dir, 0o755)
    if os.path.exists(config_path):
        # parse local_config file
        local_config = read_local_config(cfg=config_path)

        # fail to read, set to default config
        if not local_config:
            local_config = seed_config
    else:
        local_config = seed_config

except OSError as e:
    logger.exception(
        '%s: Error when attempting to access or create local log and config %s' %
        (inspect.stack()[0][3], str(e))
        )
    raise e
