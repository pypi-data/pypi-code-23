# -*- coding: utf-8 -*-
"""
Copyright François Durand
fradurand@gmail.com

This file is part of Hanabython.

    Hanabython is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Hanabython is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Hanabython.  If not, see <http://www.gnu.org/licenses/>.
"""
from hanabython.Modules.Colored import Colored
from typing import Iterable


class ConfigurationColorContents(Colored, list):
    """
    The contents of a color in a deck of Hanabi.

    This is essentially a list, stating the number of copies for each card.
    For example, [3, 2, 2, 2, 1] means there are 3 ones, 2 twos, etc.
    Each integer in this list must be strictly positive.

    :param contents: an iterable used to create the list.
    :param name: the name of the configuration. Can be None (default value).
        Should not be capitalized (e.g. "my favorite configuration" and not
        "My favorite configuration").

    >>> cfg = ConfigurationColorContents.NORMAL
    >>> print(cfg.name)
    normal
    >>> print(cfg)
    normal
    >>> print(list(cfg))
    [3, 2, 2, 2, 1]
    >>> cfg = ConfigurationColorContents([3, 2, 1])
    >>> print(cfg.name)
    None
    >>> print(cfg)
    [3, 2, 1]
    """

    def __init__(self, contents: Iterable[int], name: str = None):
        super(ConfigurationColorContents, self).__init__(contents)
        self.name = name

    def colored(self) -> str:
        if self.name is None:
            return str(list(self))
        else:
            return self.name

    #: Normal contents of a color (3 2 2 2 1).
    NORMAL = None
    #: Contents of a short color (1 1 1 1 1).
    SHORT = None


ConfigurationColorContents.NORMAL = ConfigurationColorContents(
    contents=[3, 2, 2, 2, 1], name='normal'
)
ConfigurationColorContents.SHORT = ConfigurationColorContents(
    contents=[1, 1, 1, 1, 1], name='short'
)


if __name__ == '__main__':
    my_cfg = ConfigurationColorContents.NORMAL
    my_cfg.test_str()
    print(list(my_cfg))

    print('\n')
    my_cfg = ConfigurationColorContents(
        contents=[3, 2, 1]
    )
    my_cfg.test_str()

    import doctest
    doctest.testmod()
