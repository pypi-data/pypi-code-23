# coding: utf-8

# Standard Libraries
import logging

# Cfgtree modules
from cfgtree import ConfigBaseModel
from cfgtree.cmdline_parsers.argparse import ArgparseCmdlineParser
from cfgtree.storages.anyconfig import AnyConfigStorage

log = logging.getLogger(__name__)


class AnyConfigModel(ConfigBaseModel):
    """Defines a easy to use model.

    Simple provide the configuration file to use and it will handle the load from enviroment
    variable. Use the ``AnyConfigModel`` variant to also parse command line argument.

    Usage:

    .. code-block:: python

        config = AnyConfigModel(
            model={
                "configfile": ConfigFileCfg(
                    default_filename="config.json",
                    long_param="--config-file",
                    summary="Config file"),
                # ...
            }
        )

    The ``ConfigFileCfg`` type allow to easily specify a command line argument that will be used
    to load the rest of the configuration.
    """

    environ_var_prefix = None
    """If set, defines the prefix to all environment variables that can set value in the config
    """

    cmd_line_parser = None
    """If set, define the wrapper library to use to configure the command line arguments parsing
    """

    model = None
    """Model to implement. Mandatory
    """

    def __init__(self, *args, default_config_file_name=None, **kwargs):
        stg_cfg = {
            'long_param': "--config",
            'short_param': "-c",
            'default_filename': default_config_file_name,
        }
        if self.environ_var_prefix:
            stg_cfg['environ_var'] = self.environ_var_prefix + "CONFIG_FILE"
        self.storage = AnyConfigStorage(**stg_cfg)
        super(AnyConfigModel, self).__init__(*args, **kwargs)


class AnyConfigCliModel(AnyConfigModel):
    cmd_line_parser = ArgparseCmdlineParser()
