# coding=utf-8
"""
Global context
"""
import copy
from pathlib import Path

import elib

from edlm import LOGGER

from ._settings import Settings

DEFAULT = {
    'source_folder': None,
    'paper_size': 'a4',
    'title': None,
    'markdown_text': None,
    'regen': False,

    'temp_dir': None,
    'keep_temp_dir': False,
    'media_folders': None,
    'index_file': None,
    'out_folder': None,
    'out_file': None,
    'source_file': None,

    'settings': None,
    'settings_files': None,

    'template_source': None,
    'template_file': None,

    'image_caption': None,
    'image_current': None,
    'image_extras': None,
    'image_max_width': None,
    'image_width': None,
    'image_width_str': None,
    'images_used': None,
    'images_unused': None,

    'latex_refs': None,

    'includes': None,
    'unprocessed_includes': None,
}


class _Val:
    def __init__(self, instance):
        self.instance = instance

    def _return_default(self):
        try:
            return DEFAULT[self.name]
        except KeyError:
            raise KeyError(f'CONTEXT: no default value for {self.name}')

    def __get__(self, instance, owner):
        try:
            return instance.data[self.name]
        except KeyError:
            return self._return_default()

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, self.instance):
            raise TypeError(f'CONTEXT: expected "{self.instance}" for "{self.name}", got "{type(value)}"')
        instance.data[self.name] = value

    # this is the new initializer:
    def __set_name__(self, owner, name):
        assert owner
        self.name = name  # pylint: disable=attribute-defined-outside-init


class Context:
    """
    Global context
    """
    source_folder: Path = _Val(Path)
    paper_size: str = _Val(str)
    title: str = _Val(str)
    markdown_text: str = _Val(str)

    regen: bool = _Val(bool)  # flake8: noqa

    temp_dir: Path = _Val(Path)
    keep_temp_dir: bool = _Val(bool)
    media_folders: list = _Val(list)
    index_file: Path = _Val(Path)
    out_folder: Path = _Val(Path)
    out_file: Path = _Val(Path)
    source_file: Path = _Val(Path)

    settings: Settings = _Val(Settings)
    settings_files: list = _Val(list)

    template_source: Path = _Val(Path)
    template_file: Path = _Val(Path)

    image_caption: str = _Val(str)
    image_current: str = _Val(str)
    image_extras: str = _Val(str)
    image_max_width: int = _Val(int)
    image_width: int = _Val(int)
    image_width_str: str = _Val(str)
    images_used: set = _Val(set)
    images_unused: set = _Val(set)

    latex_refs: list = _Val(list)

    includes: list = _Val(list)
    unprocessed_includes: list = _Val(list)

    def __init__(self):
        self.data = {}
        self.skip_repr = ['markdown_text']
        self.settings = Settings()

    def get_sub_context(self):
        """
        Creates a copy of this context

        Returns: new context
        """
        new_context = Context()
        new_context.data = copy.deepcopy(self.data)
        return new_context

    def debug(self, text):
        """
        Convenient shortcut to main EDLM LOGGER
        """
        if self.index_file:
            LOGGER.debug(f'"{self.index_file}": {text}')
        else:
            LOGGER.debug(f'"{self.source_folder}": {text}')

    def info(self, text):
        """
        Convenient shortcut to main EDLM LOGGER
        """
        if self.index_file:
            LOGGER.info(f'"{self.index_file}": {text}')
        else:
            LOGGER.info(f'"{self.source_folder}": {text}')

    def error(self, text):
        """
        Convenient shortcut to main EDLM LOGGER
        """
        if self.index_file:
            LOGGER.error(f'"{self.index_file}": {text}')
        else:
            LOGGER.error(f'"{self.source_folder}": {text}')

    def warning(self, text):
        """
        Convenient shortcut to main EDLM LOGGER
        """
        if self.index_file:
            LOGGER.warning(f'"{self.index_file}": {text}')
        else:
            LOGGER.warning(f'"{self.source_folder}": {text}')

    def __repr__(self):  # pylint: disable=bad-continuation
        return elib.pretty_format({k: v for k, v in self.data.items() if k not in self.skip_repr})
