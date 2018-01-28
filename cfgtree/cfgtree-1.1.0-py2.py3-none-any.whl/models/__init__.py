# coding: utf-8
"""
Configuration Tree management.
"""
# Standard Libraries
import json
import logging
import os

# Cfgtree modules
from cfgtree.dictxpath import get_node_by_xpath
from cfgtree.dictxpath import make_xpath
from cfgtree.dictxpath import set_node_by_xpath

log = logging.getLogger(__name__)

# flake8: F404


class ConfigBaseModel(object):
    """Main configuration class

    You need to inherit from this base class and implement the following members:

    - ``model``: hierarchical dictionary representing the configuration tree
    - ``environ_var_prefix``: prefix for environment variable, to avoid conflicts
    - ``storage``: class to use for configuration storage
    - ``cmd_line_parser``: which command line argument parser to use

    Usage:

    .. code-block:: python

        from cfgtree import ConfigBaseModel
        from cfgtree.cmdline_parsers.argparse import ArgparseCmdlineParser

        class MyAppConfig(ConfigBaseModel):

            # All environment variables should start by MYAPP_ to avoid collision with other
            # application's or system's environment variables
            environ_var_prefix = "MYAPP_"

            # My configuration should be read from a single JSON file
            storage = JsonConfigFile(
                # User can overwrite the configuration file name with this environment variable
                environ_var="MYAPP_COMMON_CONFIG_FILE",
                # or this command line parameter
                long_param="--config-file",
                short_param="-c",
                # If not set, search for the `config.json` file in the current directory
                default_filename="config.json",
            )

            # Use `argparse` to parse the command line
            cmd_line_parser = ArgparseCmdlineParser()

            # Here is the main settings model for the application
            model = {
                # Redefine configfile with ConfigFileCfg so that it appears in --help
                "configfile": ConfigFileCfg(long_param="--config-file",
                                            short_param="-c",
                                            summary="Configuration file"),

                # can holds a version information for the storage file
                "version": VersionCfg(),

                "general": {
                    "verbose": BoolCfg(short_param='-v',
                                       long_param="--verbose",
                                       summary='Enable verbose output logs'),
                    "logfile":
                        StringCfg(short_param="-l",
                                  summary='Output log to file'),
                },
            }

        # As an example, the 'verbose' setting can then be configured by:
        #  - environment variable "MYAPP_GENERAL_VERBOSE"
        #  - command line option ``--verbose`
        #  - key ``general.verbose`` in configuration file ``config.json``

        cfg = MyAppConfig()
        # Read
        cfg.get_cfg_value("group1.dict_opt.key1")
        # Write
        cfg.set_cfg_value("group1.dict_opt.key1", "newval")

    """

    model = None
    """Main configuration tree model"""

    environ_var_prefix = None
    """Prefix for all environment variable (to avoid conflict with other app)

    Example::

        environ_var_prefix="MYAPP_"
    """

    storage = None
    """Configuration storage class to use with this model

    Should be a class inheriting from ConfigBaseStorage"""

    cmd_line_parser = None
    """Command line parser to use.

    Should be a class inheriting from CmdlineParsersBase"""

    def __init__(self, model=None, environ_var_prefix=None, storage=None, cmd_line_parser=None):
        """Construct your configuration object

        Optional arguments.
            model ([type], optional): Defaults to None. Model to define
            environ_var_prefix ([type], optional): Defaults to None. environment variable prefix
            storage ([type], optional): Defaults to None. storage class
            cmd_line_parser ([type], optional): Defaults to None. command line parser
        """
        if model and self.model is None:
            self.model = model
        if environ_var_prefix and self.environ_var_prefix is None:
            self.environ_var_prefix = environ_var_prefix
        if storage and self.storage is None:
            self.storage = storage
        if cmd_line_parser and self.cmd_line_parser is None:
            self.cmd_line_parser = cmd_line_parser
        self._inject_names()

    def _inject_names(self, root=None, xpath=None):
        """
        Inject configuration item name defined in the cfgtree dict inside each `_Cfg`.
        """
        if root is None:
            if self.model is None:
                return
            root = self.model
        # pylint: disable=no-member
        for name, item in root.items():
            if isinstance(item, dict):
                self._inject_names(root=item, xpath=make_xpath(xpath, name))
            else:
                item.name = name
                item.xpath = make_xpath(xpath, name)
                item.environ_var_prefix = self.environ_var_prefix
                if item.ignore_in_cfg:
                    # log.debug("Create cfg node '%s': ignored (handled later)", item.xpath)
                    continue
                log.debug("Create cfg node: '%s' (name: '%s', cmd line: '%s'), default  : %r",
                          item.xpath, item.name, item.long_param, item.safe_value)
        # pylint: enable=no-member

    def set_cfg_value(self, xpath, value):
        """
        Set a value in cfgtree.
        """
        set_node_by_xpath(self.model, xpath, value, extend=True, setter_attr="set_value")

    def get_cfg_value(self, xpath, default=None):
        """
        Get a value from cfgtree.
        """
        return get_node_by_xpath(self.model, xpath, default=default).value

    def find_configuration_values(self, argv=None):
        """Main cfgtree entrypoint"""
        self._load_configuration(argv=argv)
        self._load_environment_variables("", self.model)
        self._load_cmd_line_arg(argv)

    def _load_cmd_line_arg(self, argv=None):
        if self.cmd_line_parser:
            self.cmd_line_parser.parse_cmd_line(self.model, argv)

    def _load_configuration(self, argv=None):
        log.debug("Looking for configuration")
        self.storage.find_storage(self.model, argv=argv)
        bare_cfg = self.storage.get_bare_config_dict()
        self._load_cfg_dict(bare_cfg)

    def save_configuration(self):
        """Save configuration to storage"""
        log.debug("Saving configuration file")
        bare_cfg = self._dict(safe=False)
        self.storage.save_bare_config_dict(bare_cfg)

    def _load_cfg_dict(self, cfg, xpath=None):
        for k, v in cfg.items():
            xp = make_xpath(xpath, k)
            if isinstance(v, dict):
                self._load_cfg_dict(v, xp)
            else:
                try:
                    self.set_cfg_value(xp, v)
                except KeyError:
                    log.error("Unable to load value '%s' from configuration file, "
                              "no matching item in configuration tree (invalid '%s')", k, xp)

    def _load_environment_variables(self, xpath, root):
        """
        Inject value from environment variable.
        """
        for name, item in root.items():
            if isinstance(item, dict):
                self._load_environment_variables(make_xpath(xpath, name), item)
            elif item.environ_var and item.environ_var in os.environ:
                if item.ignore_in_cfg:
                    log.debug("Ignoring environment variable %s", item.environ_var)
                val = item.read_environ_var()
                log.debug("Found environment variable '%s': %s (conf: %s)", item.environ_var, val,
                          item.xpath)
                item.value = val

    def _dict(self, root=None, safe=False):
        """
        Return the configuration as a dictionnary.
        """
        if root is None:
            root = self.model
        d = {}
        # pylint: disable=no-member
        for name, item in root.items():
            if isinstance(item, dict):
                d[name] = self._dict(root=item, safe=safe)
            else:
                if item.ignore_in_cfg:
                    continue
                elif safe:
                    d[name] = item.safe_value
                else:
                    d[name] = item.value
        # pylint: enable=no-member
        return d

    def json(self, safe=False):
        """Dumps current configuration tree into a human readable json"""
        return json.dumps(self._dict(safe=safe), sort_keys=True, indent=4, separators=(',', ': '))
