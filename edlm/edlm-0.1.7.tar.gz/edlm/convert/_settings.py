# coding=utf-8
"""
Per-document settings
"""

import collections

import elib

# noinspection SpellCheckingInspection
DEFAULT = {
    'papersize': ['a4'],
    'aliases': dict(),
    'references': dict(),
    'links': {
        'breaklinks': 'true',
        'bookmarks': 'true',
        'bookmarksopen': 'true',
        'linkcolor': "Grey",
        'citecolor': "Grey",
        'urlcolor': "Grey",
        'anchorcolor': "Grey",
        'filecolor': "Grey",
        'menucolor': "Grey",
        'runcolor': "Grey",
    }
}


class _Val:

    def __init__(self, instance):
        self.instance = instance

    def _return_default(self):
        try:
            return DEFAULT[self.name]
        except KeyError:
            raise KeyError(f'SETTINGS: no default value for {self.name}')

    def __get__(self, instance, owner):
        try:
            return instance.data[self.name]
        except KeyError:
            return self._return_default()

    def __set__(self, instance, value):
        if not isinstance(value, self.instance):
            raise TypeError(f'SETTINGS: expected "{self.instance}" for "{self.name}"')
        instance.data[self.name] = value

    # this is the new initializer:
    def __set_name__(self, owner, name):
        assert owner
        self.name = name  # pylint: disable=attribute-defined-outside-init


class Settings:
    """
    Per-document settings
    """
    papersize: list = _Val(list)
    aliases: dict = _Val(dict)
    references: dict = _Val(dict)
    links: dict = _Val(dict)

    def __init__(self):
        self.data = {}

    @staticmethod
    def _update_nested_dict(source_dict, updated_dict) -> collections.Mapping:
        """
        Updates a dictionary from another

        Args:
            source_dict: source dictionary (will be overwritten)
            updated_dict: updated dictionary (will take precedence)

        Returns: merged dictionary

        """
        for key, value in updated_dict.items():
            if isinstance(value, collections.Mapping):
                result = Settings._update_nested_dict(source_dict.get(key, {}), value)
                source_dict[key] = result
            else:
                source_dict[key] = updated_dict[key]
        return source_dict

    def update(self, other_dict: collections.Mapping):
        """
        Update these settings with another dictionary

        The other dictionary will have precedence

        Args:
            other_dict: dictionary to update from
        """
        self.data = self._update_nested_dict(self.data, other_dict)

    def __repr__(self) -> str:
        return "Settings:\n" + elib.pretty_format(self.data)
