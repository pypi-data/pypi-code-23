# encoding: utf-8

# Get module version
from ._metadata import __version__

# Import key items from module
import configurationutil.configuration as cfg_params

from configurationutil.configuration import (
    Configuration
)

from configurationutil.cfg_providers import (
    JSONConfig,
    YAMLConfig
)

from configurationutil.cfg_objects import (
    CfgItem,
    CfgItems,
    InheritableCfgItem,
    ContainerCfgItem,
    ContainerItemDefaults
)

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
