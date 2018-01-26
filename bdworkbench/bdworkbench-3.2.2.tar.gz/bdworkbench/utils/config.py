#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function

import os
import ConfigParser

KEY_BASE = 'base'
KEY_SDKBASE = 'sdkbase'
KEY_DELIVERABLES = 'deliverables_dir'

KEY_LOGDIR = 'log_dir'
KEY_IMAGEDIR = 'image_dir'
KEY_STAGEDIR = 'staging_dir'
KEY_APPCONFIGDIR = 'appconfig_dir'

KEY_DEF_ORGNAME = 'def_orgname'

SECTION_WB = 'workbench'

DIRNAME = os.path.dirname(os.path.realpath(__file__))
SDK_BASE_DIR = os.path.abspath(os.path.join(DIRNAME, '..'))

class WBConfig(object):
    """

    """

    def __init__(self):
        """
        """
        cwd = os.getcwd()
        self.config = ConfigParser.SafeConfigParser()
        self.config.add_section(SECTION_WB)

        if os.getenv('USE_BDS_INTERNAL_ORGNAME', 'false') == 'true':
            orgname = 'bluedata'
        else:
            orgname = None

        self.defaults = {
                         KEY_BASE: cwd,
                         KEY_DEF_ORGNAME: orgname,
                         KEY_SDKBASE: SDK_BASE_DIR,
                         KEY_LOGDIR: os.path.join(cwd, "logs"),
                         KEY_IMAGEDIR: os.path.join(cwd, "image"),
                         KEY_STAGEDIR: os.path.join(cwd, "staging"),
                         KEY_APPCONFIGDIR: os.path.join(cwd, "appconfig"),
                         KEY_DELIVERABLES: os.path.join(cwd, "deliverables")
                        }

    def _save(self):
        """
        Save the modified config params.
        """
        return

    def get(self, section, key, default=None):
        """

        """
        try:
            return self.config.get(section, key, vars=self.defaults)
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            return default

    def addOrUpdate(self, section, key, value):
        """

        """
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, str(value))
        self._save()

__all__ = ['WBConfig', 'KEY_BASE', 'KEY_SDKBASE', 'KEY_LOGDIR', 'KEY_IMAGEDIR',
           'KEY_COMPSDIR', 'KEY_APPCONFIGDIR', 'SECTION_WB']
