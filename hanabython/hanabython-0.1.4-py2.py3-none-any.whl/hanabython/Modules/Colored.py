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
from hanabython.Modules.StringUtils import uncolor


class Colored:
    r"""
    An object with a colored string representation.

    >>> from hanabython.Modules.StringAnsi import StringAnsi
    >>> class MyClass(Colored):
    ...     def colored(self):
    ...         return StringAnsi.RED + 'some text' + StringAnsi.RESET
    >>> my_object = MyClass()
    >>> my_object.colored()
    '\x1b[31msome text\x1b[0;0m'
    >>> str(my_object)
    'some text'
    >>> repr(my_object)
    '<MyClass: some text>'
    """

    def __repr__(self) -> str:
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self) -> str:
        return uncolor(self.colored())

    def colored(self) -> str:
        """
        Colored version of :meth:`__str__`.

        In the subclasses, the principle is to override only this method.
        :meth:`__str__` is automatically defined as the uncolored version of
        the same string, and :meth:`__repr__` as the same with the class name
        added.

        Of course, it is also possible to override :meth:`__str__` and/or
        :meth:`__repr__` if a different behavior is desired.

        :return: a string representing the object, possibly with ANSI escape
            codes to add colors and style.
        :rtype: str
        """
        pass

    def test_str(self) -> None:
        """
        Test the string representations of the object.

        Print the results of :meth:`__repr__`, :meth:`__str__` and
        :meth:`colored`.
        """
        print('repr:')
        print(repr(self))
        print('\nstr:')
        print(self)
        print('\ncolored:')
        print(self.colored())


if __name__ == '__main__':
    from hanabython.Modules.StringAnsi import StringAnsi

    class TestClass(Colored):
        def colored(self):
            return StringAnsi.RED + 'some text' + StringAnsi.RESET
    test_object = TestClass()
    test_object.test_str()

    import doctest
    doctest.testmod()
