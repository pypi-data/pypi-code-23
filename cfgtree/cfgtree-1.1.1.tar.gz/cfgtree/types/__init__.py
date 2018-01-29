# coding: utf-8

# Standard Libraries
import argparse
from typing import Any
import logging
import os

log = logging.getLogger(__name__)
_UNDEFINED = object()

# flake8: E741


class _CfgBase(object):

    default = None  # type: Any
    """Default value"""

    name = None  # type: str
    """name of the item"""

    xpath = None  # type: atr
    """xpath to reach this element"""

    arg_type = None  # type: str
    """argument type"""

    environ_var_prefix = None  # type: str
    """prefix to use for environemn"""

    ignore_in_cfg = False  # type: bool
    """ """

    ignore_in_args = False  # type: bool
    """ """

    ignore_in_envvars = False  # type: bool
    """ """

    def __init__(self,
                 long_param: str = None,
                 description: str = None,
                 short_param: str = None,
                 summary: str = None,
                 required: bool = False,
                 default: Any = _UNDEFINED):
        # Note: self.name should come later by ConfigBaseModel._inject_names()
        self.short_param = short_param
        self.summary = summary
        self.description = description
        self.required = required
        self.forced_long_param = long_param
        if default != _UNDEFINED:
            self.default = default
        self._value = self.default

    def set_value(self, value):
        """
        Setter method used in `set_node_by_xpath`.
        """
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.set_value(value)

    @property
    def environ_var(self):
        if self.environ_var_prefix:
            return self.environ_var_prefix + self.cmd_line_name.upper()

    def get_cmd_line_params(self):
        a = []
        if self.short_param:
            a.append(self.short_param)
        if self.name:
            a.append(self.long_param)
        return a

    @property
    def _environ_var_value(self):
        return os.environ.get(self.environ_var, _UNDEFINED)

    def read_environ_var(self):
        return str(self._environ_var_value)

    @property
    def long_param(self):
        if self.forced_long_param:
            return self.forced_long_param
        if not self.xpath:
            return "--" + self.name.lower().replace("_", "-")
        return "--" + self.xpath.replace('.', '-').replace('_', '-')

    @property
    def cmd_line_name(self):
        return self.xpath.lower().replace("-", "_").replace(".", "_")

    @property
    def action(self):
        return 'store'

    @property
    def n_args(self):
        return None

    @property
    def safe_value(self):
        """
        Return value as a string without compromizing information.
        """
        return self.value

    @property
    def cfgfile_value(self):
        """
        Return value to save in config file.
        """
        return self.value if self.value is not None else ""

    @property
    def metavar(self):
        return self.name.upper()


class StringCfg(_CfgBase):
    """String value

    Example::

        "a value"
    """
    default = ""

    def read_environ_var(self):
        return str(self._environ_var_value)


class IPCfg(StringCfg):
    """IPv4 or IPv6 value

    Example::

        "192.168.0.1"
    """


class ListOfStringCfg(_CfgBase):
    """
    Comma separated list of string (1 argument).

    Example::

        "a,b,c,d"
    """

    def __init__(self, *args, **kwargs):
        self.default = []
        super(ListOfStringCfg, self).__init__(*args, **kwargs)

    def read_environ_var(self):
        ls = self._environ_var_value
        return ls.split(",")

    @property
    def cfgfile_value(self):
        """
        Return value to save in config file.
        """
        return ",".join(self.value)

    @staticmethod
    def arg_type(string):
        return string.split(",")


class IntCfg(_CfgBase):
    """Integer value

    Example::

        123
    """

    default = 0

    def read_environ_var(self):
        return int(self._environ_var_value)


class PortCfg(IntCfg):
    """Port value, with range from 1 to 65535

    Example::

        49670
    """


class FloatCfg(_CfgBase):
    """Float or double value

    Example::

        1,23
    """
    default = 0

    def read_environ_var(self):
        return float(self._environ_var_value)


class HardcodedCfg(_CfgBase):
    """
    Placeholder only used to store application value.

    It does not present an environment variable nor a command line argument.
    """

    default = None
    ignore_in_args = True
    ignore_in_envvars = True

    def get_cmd_line_params(self):
        return []

    def read_environ_var(self):
        return None

    @property
    def long_param(self):
        return None


class ConfigVersionCfg(HardcodedCfg):
    """
    Version of the configuration storage.

    It does not present an environment variable nor a command line argument

    Example::

        "1.2.3"
    """


class PasswordCfg(StringCfg):
    """Password value

    This can be used to handle value while limiting its exposition
    """

    @property
    def password(self):
        return self.value

    @property
    def safe_value(self):
        """
        Hide password in logs.
        """
        return "*" * len(self.value)


class DirNameCfg(StringCfg):
    """Directory name

    Example::

        "/path/to/existing/folder"
    """

    default = None

    def set_value(self, value):
        self._value = os.path.abspath(value)


class ConfigFileCfg(StringCfg):
    """Configuration file to load rest of configuration

    Use to tell to your storage where the rest of the configuration should be used

    Example::

        "/path/to/my/config.json"
    """
    default = None
    ignore_in_cfg = True

    def __init__(self, *args, default_filename=None, **kwargs):
        self.default_filename = default_filename
        super(ConfigFileCfg, self).__init__(*args, **kwargs)


class BoolCfg(_CfgBase):
    """Boolean value

    Handle automatic integer convertion
    Example::

        True
    """
    default = False  # type: Any

    def read_environ_var(self):
        e = os.environ.get(self.environ_var)
        return bool(e)

    @property
    def action(self):
        return 'store_true'

    @property
    def metavar(self):
        return None


class MultiChoiceCfg(ListOfStringCfg):
    """Let user choose one or mode value between several string value

    Example::

        "a_value"
    """

    def __init__(self, *args, choices=None, **kwargs):
        super(MultiChoiceCfg, self).__init__(*args, **kwargs)
        self.choices = choices

    def arg_type(self, string):
        items = string.split(",")
        for item in items:
            if item not in self.choices:
                raise argparse.ArgumentTypeError("{!r} not in available choise: {}".format(
                    item, ", ".join(self.choices)))
        return items


class SingleChoiceCfg(StringCfg):
    """Let user choose one value between several string value

    Example::

        "a_value"
    """

    def __init__(self, *args, choices=None, **kwargs):
        super(SingleChoiceCfg, self).__init__(*args, **kwargs)
        self.choices = choices

    def arg_type(self, string):
        if string not in self.choices:
            raise argparse.ArgumentTypeError("{!r} not in available choise: {}".format(
                string, ", ".join(self.choices)))
        return string
