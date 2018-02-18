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

    @elib.config.ConfigProp(str, default='./miktex.7z')
    def miktex_archive(self):
        """
        Path as a string to Miktex archive
        """
        pass

    @elib.config.ConfigProp(str, default='./miktex')
    def miktex_path(self):
        """
        Path as a string to Miktex installation folder
        """
        pass

    @elib.config.ConfigProp(str, default='./pandoc.7z')
    def pandoc_archive(self):
        """
        Path as a string to Pandoc installation folder
        """
        pass

    @elib.config.ConfigProp(str, default='./pandoc')
    def pandoc_path(self):
        """
        Path as a string to Pandoc installation folder
        """
        pass

    @elib.config.ConfigProp(parser=bool, default=False)
    def debug(self):
        """
        Sets logging level to DEBUG for the console
        """
        pass

    @elib.config.ConfigProp(parser=bool, default=False)
    def keep_temp_dir(self):
        """
        Do not delete temp dir after a successful convert operation
        """
        pass


CFG = Config()
