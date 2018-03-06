# -*- coding: utf-8 -*-


__all__ = (
    'MissingFile',
)


class MissingFile(Exception):
    """Used when the `collection.xml` or `index.cnxml` file is missing."""
