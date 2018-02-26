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
from hanabython.Modules.Action import Action
from hanabython.Modules.StringAnsi import StringAnsi


class ActionForfeit(Action):
    """
    An action of a player: forfeit (lose the game immediately).

    >>> action = ActionForfeit()
    >>> print(action)
    Forfeit
    """

    def __init__(self):
        super().__init__(Action.FORFEIT)

    def colored(self) -> str:
        return (StringAnsi.RED + StringAnsi.STYLE_BOLD
                + 'Forfeit' + StringAnsi.RESET)


if __name__ == '__main__':
    my_action = ActionForfeit()
    my_action.test_str()

    import doctest
    doctest.testmod()
