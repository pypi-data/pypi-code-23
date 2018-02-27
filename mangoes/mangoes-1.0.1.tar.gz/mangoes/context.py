# -*-coding:utf-8 -*
"""Definitions a the context of a word in a sentence

This module defines classes to be used as `context_definition` parameter in the
:func:`mangoes.counting.count_cooccurrence` function.

Examples
--------

    >>> window_3 = mangoes.context.Window(window_half_size=3)
    >>> window_3(4, ['The', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog'])
    ['quick', 'brown', 'fox', 'over', 'the', 'lazy']
    >>> window_3(5, ['The', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog'])
    ['brown', 'fox', 'jumps', 'the', 'lazy', 'dog']
    >>> window_3(7, ['The', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog'])
    ['jumps', 'over', 'the', 'dog']

"""
import abc
import logging
import random

_logger = logging.getLogger(__name__)


class Context:
    """Base callable class to define the context of a word in a sentence

    See Also
    --------
    :func:`mangoes.counting.count_cooccurrence`
    """
    def __init__(self):
        self._params = {}

    @abc.abstractmethod
    def __call__(self, position, sentence):
        """Returns the elements in the defined context

        This function extracts the list of elements found in the context of the element in the given position
        of a sentence

        Parameters
        ----------
        position: int
            position in the sentence of the word whose contexts list is wanted
        sentence: list

        Returns
        -------
        list
        """
        pass

    @property
    def params(self):
        """Parameters of the context"""
        return self._params


class Window(Context):
    """Implements window-type context

    Parameters
    ----------
    symmetric: boolean (def = True)
        if the window is symmetric (default), the window will be centered around the position, and window_half_size
        must be an integer.

    window_half_size: int if symmetric, tuple of 2 int if not
        size of the search space to the left and to the right of 'position' word (default = 1)

    dirty: boolean (def = False)
        if True and some of the words in the window aren't correct ids (ex : -1), they will not be fetched, but the
        window will be extended further so as to still be able to meet the quota of 2*'window_half_size' (if
        symmetric) words to fetch.

    dynamic: boolean
        if True, the size of the actual window is sampled between 1 and `window_half_size`

    Returns
    -------
    list or callable
    """
    def __init__(self, symmetric=True, window_half_size=1, dirty=False, dynamic=False):
        super().__init__()
        self._params.update({"symmetric": symmetric, "window_half_size": window_half_size, "dirty": dirty,
                             "dynamic": dynamic})

        if symmetric:
            self.size_before = self.size_after = window_half_size
        else:
            self.size_before, self.size_after = window_half_size

        if dirty:
            if dynamic:
                self._window = _window_dirty_dynamic
            else:
                self._window = _window_dirty
        else:
            if dynamic:
                self._window = _window_clean_dynamic
            else:
                self._window = _window_clean

    def __call__(self, position, sentence):
        """Returns the elements in the defined window

        This function extracts the list of elements found in a window defined around the given position, barring the
        element at the given position itself.

        Parameters
        ----------
        position: int
            position in the sentence of the word whose contexts list is wanted
        sentence: list

        Returns
        -------
        list
        """

        return self._window(position, sentence, self.size_before, self.size_after)


def _window_clean(position, sentence, size_before=0, size_after=1):
    before_list = [w for w in sentence[max(0, position - size_before):position] if w != -1]
    after_list = [w for w in sentence[position + 1:min(position + size_after + 1, len(sentence))] if w != -1]
    return before_list + after_list


def _window_clean_dynamic(position, sentence, max_size_before=0, max_size_after=1):
    size_before, size_after = _get_random_size(max_size_before, max_size_after)
    return _window_clean(position, sentence, size_before, size_after)


def _window_dirty(index, sentence, size_before=0, size_after=1):
    before_list = []
    after_list = []

    i = index - 1
    while i >= 0 and len(before_list) < size_before:
        if sentence[i] > -1:
            before_list.append(sentence[i])
        i -= 1
    before_list = list(reversed(before_list))

    i = index + 1
    while i < len(sentence) and len(after_list) < size_after:
        if sentence[i] > -1:
            after_list.append(sentence[i])
        i += 1

    return before_list + after_list


def _window_dirty_dynamic(index, sentence, max_size_before=0, max_size_after=1):
    size_before, size_after = _get_random_size(max_size_before, max_size_after)
    return _window_dirty(index, sentence, size_before, size_after)


def _get_random_size(max_size_before, max_size_after):
    size_before = random.randint(1, max_size_before) if max_size_before > 0 else 0
    if max_size_after == max_size_before:
        size_after = size_before
    else:
        size_after = random.randint(1, max_size_after) if max_size_after > 0 else 0
    return size_before, size_after
