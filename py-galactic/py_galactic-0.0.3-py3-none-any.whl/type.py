"""
A type is associated to an :class:`Attribute <galactic.context.Attribute>`. A type is valid if it is
a class that can be called

* without argument: in that case a default value is returned for that type
* with an argument: in that case, the class try to convert it to an acceptable value

For example the :class:`int` and :class:`bool` classes are acceptable types as they accept to be
called without arguments or with an argument which is converted to the desired type.

This module defines several types useful in :class:`Context` values:

* :class:`Category` created with a call to the :func:`category` function;
* :class:`ImpreciseCategory` created with a call to the :func:`imprecise_category` function
"""
from typing import Iterable, Set, MutableSet, Iterator, Mapping, MutableMapping

from bitstring import BitArray


class ImpreciseCategory(MutableSet[object],metaclass=type):
    """
    The :class:`ImpreciseCategory` class defines a generic way to create new classes over an
    imprecise category of values.
    """
    _items: Mapping[object, int] = {}
    _instances: Mapping[BitArray, 'ImpreciseCategory']
    _cache: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._cache:
            pass
        else:
            return super().__new__(cls, *args, **kwargs)

    def __init__(self, items: Iterable[object] = None):
        """
        Initialise a :class:`ImpreciseCategory`.

        Parameters
        ----------
            items : :class:`Iterable[object] <python:collections.abc.Iterable>`
                an iterable of object

        .. versionadded:: 0.0.2
        """
        self._bits = BitArray(length=len(type(self)._items))
        if items is not None:
            for item in items:
                self.add(item)

    def add(self, item: object) -> None:
        """
        Add a value to the category

        Parameters
        ----------
            item : :class:`object`
                the item to add

        Raises
        ------
            ValueError
                if the item is not contained in the category class

        .. versionadded:: 0.0.2
        """
        if item in type(self)._items:
            self._bits[type(self)._items[item]] = True
        else:
            raise ValueError

    def discard(self, item: object) -> None:
        """
        Remove an item from the category.

        Parameters
        ----------
            item : :class:`object`
                the item to discard

        Raises
        ------
            ValueError
                if the item is not contained in the category class

        .. versionadded:: 0.0.2
        """
        if item in type(self)._items:
            self._bits[type(self)._items[item]] = False
        else:
            raise ValueError

    def __contains__(self, item: object) -> bool:
        """
        Test if an item is in the category.

        Parameters
        ----------
            item : :class:`object`
                the item to test

        Returns
        -------
            :class:`bool`
                True if the item is in the category

        Raises
        ------
            ValueError
                if the item is not contained in the category class

        .. versionadded:: 0.0.2
        """
        if item in type(self)._items:
            return self._bits[type(self)._items[item]]
        else:
            raise ValueError

    def __len__(self) -> int:
        """
        Get the number of items in the category.

        Returns
        -------
            the number of items in the category : :class:`int`

        .. versionadded:: 0.0.2
        """
        return self._bits.count(True)

    def __iter__(self) -> Iterator[object]:
        """
        Get an iterator over the items in the category.

        Returns
        -------
            an iterator : :class:`Iterator[object] <python:collections.abc.Iterator>`

        .. versionadded:: 0.0.2
        """
        for item, index in type(self)._items.items():
            if self._bits[index]:
                yield item

    def __str__(self) -> str:
        """
        Convert this category to a readable string.

        Returns
        -------
            the user friendly readable string of this category : :class:`str`

        .. versionadded:: 0.0.2
        """
        return str([item for item in self])


def imprecise_category(name, iterable: Iterable[object] = None, module: str = None):
    """
    This function create a new dynamic class derived from the :class:`ImpreciseCategory` class.

    Example
    -------

        >>> from galactic.type import imprecise_category
        >>> Color = imprecise_category('Color', ['R', 'G', 'B'])

    The returned value of :func:`imprecise_category` is a class.

    Example
    -------

        >>> type(Color)
        <class 'typing.GenericMeta'>

    Its representable string is constructed using its name.

    Example
    -------

        >>> print(Color)
        __main__.Color

    A new imprecise category constructed by calling the class without argument has no possible
    values.

    Example
    -------

        >>> print(Color())
        []
        >>> print(Color(['R']))
        ['R']

    Element membership can be tested as for any set.

    Example
    -------

        >>> color = Color(['R', 'B'])
        >>> print(color)
        ['R', 'B']
        >>> print('B' in color)
        True

    Elements can be iterated and it's possible to know their length.

    Example
    -------

        >>> [item for item in color]
        ['R', 'B']
        >>> print(len(color))
        2

    It's possible to add and remove elements.

    Example
    -------

        >>> color = Color()
        >>> color.add('B')
        >>> color.add('R')
        >>> print(color)
        ['R', 'B']
        >>> color.discard('R')
        >>> print(color)
        ['B']

    The class can be created in a specific module:

    Example
    -------

        >>> Color = imprecise_category('Color', ['R', 'G', 'B'], 'mymodule')
        >>> print(Color)
        mymodule.Color

    Parameters
    ----------
        name : :class:`str`
            the name of the new class
        iterable : :class:`Iterable <python:collections.abc.Iterable>`
            an iterable collection of values
        module : :class:`str`
            the module name (the current module is used if this key is not precised)

    Returns
    -------
        a new class : :class:`type <python:type>`

    .. versionadded:: 0.0.2
    """
    if iterable is None:
        iterable = []
    items = {item: index for item, index in zip(iterable, range(len(iterable)))}

    if module is None:
        import inspect
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        if mod is None:
            module = '__main__'
        else:
            module = mod.__name__
    else:
        module = str(module)

    return type(
        str(name),
        (ImpreciseCategory,),
        {
            '_items': items,
            '__metaclass__': type,
            '__module__': module
        }
    )


class Category(object):
    """
    The :class:`Category` class defines a generic way to create new classes over a category of
    values.
    """
    _items: Mapping[object, int] = {}
    _instances: MutableMapping[int, 'Category'] = None

    def __new__(cls, value: object = None):
        if cls._instances is None:
            cls._instances = {}
            for item, index in cls._items.items():
                cls._instances[index] = super().__new__(cls)
                cls._instances[index]._item = item
        if value in cls._items:
            return cls._instances[cls._items[value]]
        elif value is None:
            return cls._instances[0]
        else:
            raise ValueError

    def __init__(self):
        self._item = None

    def __str__(self) -> str:
        """
        Convert this category to a readable string.

        Returns
        -------
            the user friendly readable string of this category : :class:`str`

        .. versionadded:: 0.0.2
        """
        return str(self._item)


def category(name, iterable: Iterable[object] = None, module: str = None):
    """
    This function create a new dynamic class derived from the :class:`Category` class.

    Example
    -------

        >>> from galactic.type import category
        >>> Color = category('Color', ['R', 'G', 'B'])

    The returned value of :func:`category` is a class.

    Example
    -------

        >>> type(Color)
        <class 'type'>

    Its representable string is constructed using its name.

    Example
    -------

        >>> print(Color)
        <class '__main__.Color'>

    A new category constructed by calling the class without argument has the first value.

    Example
    -------

        >>> print(Color())
        []
        >>> print(Color('R'))
        'R'

    Element membership can be tested as for any set.

    Example
    -------

        >>> color = Color(['R', 'B'])
        >>> print(color)
        ['R', 'B']
        >>> print('B' in color)
        True

    Elements can be iterated and it's possible to know their length.

    Example
    -------

        >>> [item for item in color]
        ['R', 'B']
        >>> print(len(color))
        2

    It's possible to add and remove elements.

    Example
    -------

        >>> color = Color()
        >>> color.add('B')
        >>> color.add('R')
        >>> print(color)
        ['R', 'B']
        >>> color.discard('R')
        >>> print(color)
        ['B']

    The class can be created in a specific module:

    Example
    -------

        >>> Color = category('Color', ['R', 'G', 'B'], 'mymodule')
        >>> print(Color)
        mymodule.Color

    Parameters
    ----------
        name : :class:`str`
            the name of the new class
        iterable : :class:`Iterable <python:collections.abc.Iterable>`
            an iterable collection of values
        module : :class:`str`
            the module name (the current module is used if this key is not precised)

    Returns
    -------
        a new class : :class:`type <python:type>`

    .. versionadded:: 0.0.2
    """
    if iterable is None:
        iterable = []
    items = {item: index for item, index in zip(iterable, range(len(iterable)))}
    if not bool(items):
        raise ValueError

    if module is None:
        import inspect
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        if mod is None:
            module = '__main__'
        else:
            module = mod.__name__
    else:
        module = str(module)

    return type(
        str(name),
        (Category,),
        {
            '_items': items,
            '__module__': module
        }
    )
