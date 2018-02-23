# coding=utf-8
"""
EDLM configuration
"""

import elib


class Config(elib.config.BaseConfig):
    """
    EDLM configuration
    """

    def __init__(self):
        elib.config.BaseConfig.__init__(self, __package__)

    miktex_archive = elib.config.ConfigProp(str, default='./miktex.7z')
    miktex_path = elib.config.ConfigProp(str, default='./miktex')
    pandoc_archive = elib.config.ConfigProp(str, default='./pandoc.7z')
    pandoc_path = elib.config.ConfigProp(str, default='./pandoc')
    debug = elib.config.ConfigProp(parser=bool, default='false')
    keep_temp_dir = elib.config.ConfigProp(parser=bool, default='false')


CFG = Config()
