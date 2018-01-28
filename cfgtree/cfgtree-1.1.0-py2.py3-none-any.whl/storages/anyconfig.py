# coding: utf-8

# Standard Libraries
import logging
from pathlib import Path
from typing import Dict

# Third Party Libraries
import anyconfig

# Cfgtree modules
from cfgtree.storages._single_file import SingleFileStorage

log = logging.getLogger(__name__)


class AnyConfigStorage(SingleFileStorage):
    """
    Settings are stored in a single file handled by AnyConfig.

    Supported file formats:

    - JSON
    - INI
    - YAML (if ruamel.yaml is installed)
    - TOML (if toml is installed)

    Usage:

    .. code-block:: python

        class MyAppConfig(ConfigBaseModel):

            environ_var_prefix = "MYAPP_"

            storage = AnyConfigStorage(
                environ_var="MYAPP_COMMON_CONFIG_FILE",
                long_param="--config",
                short_param="-c",
                default_filename="config.json",
            )

            cmd_line_parser = # ...

            model = {
                # repeat in model so the arguments in described in --help
                "configfile": ConfigFileCfg(long_param="--config-file", summary="Config file"),
                # ...
            }

    """

    default_filename = None
    """Default filename for the configuration file

    Example::

        myconfig.json
    """

    environ_var = None
    """Environment variable to set the configuration file name

    Example::

       DOPPLERR_COMMON_CONFIG_FILE="myconfig.json"
    """

    short_param = None
    """Short parameter to specify the configure file name

    Example::

        -g myconfig.json
    """

    long_param = None
    """Short parameter to specify the configure file name

    Example::

        --config-file myconfig.json
    """

    def load_bare_config(self, config_file_path: Path):
        return anyconfig.load(config_file_path.absolute().as_posix())

    def save_bare_config_dict(self, bare_cfg: Dict):
        return anyconfig.dump(bare_cfg, self.__resolved_config_file)
