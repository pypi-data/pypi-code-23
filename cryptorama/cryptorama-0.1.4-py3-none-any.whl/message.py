#   This file is part of the program cryptorama.
#
#   Copyright (C) 2017 by Bonnie Saunders, Marc Culler and others. 
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   Project homepage: https://bitbucket.org/bonnie_saunders/cryptorama/
#   Author homepage: https://math.uic.edu/~saunders
#   Author homepage: https://marc-culler.info

import re
from itertools import cycle, groupby
from .alphabet import Alphabet, Substitution, big, small

class MessageMeta(type):
    """
    Metaclass for constructing the Message class.
    """
    # Methods of str which will be modified to return a Message.
    str_methods = ['__format__', '__getitem__', '__mod__', '__mul__',  'rmod__', '__rmul__',
                   'capitalize', 'casefold', 'center', 'endswith', 'expandtabs',
                   'format', 'format_map', 'join', 'ljust', 'lower', 'lstrip',
                   'replace', 'rjust', 'rstrip', 'startswith', 'strip', 'swapcase',
                   'title', 'translate', 'upper', 'zfill']
    tuple_methods = ['partition', 'rpartition']
    list_methods = ['split', 'splitlines', 'rsplit']
    
    def __new__(cls, name, bases, attrs):
        result = super(MessageMeta, cls).__new__(cls, name, bases, attrs)
        for method in cls.str_methods:
            setattr(result, method, cls._extend_str(method))
        for method in cls.tuple_methods:
            setattr(result, method, cls._extend_seq(method, tuple))
        for method in cls.list_methods:
            setattr(result, method, cls._extend_seq(method, list))
        return result

    @staticmethod
    def _extend_str(method_name):
        """
        Convert a method of str returning a str into a method returning
        a Message with the same alphabet as self.
        """
        def extended(self, *args, **kwargs):
            s = getattr(str, method_name)(self, *args, **kwargs)
            return Message(s, self.alphabet)
        return extended

    @staticmethod
    def _extend_seq(method_name, seq_type):
        """
        Convert a method of str returning a sequence of str objects into a
        method returning a sequence of Message objects with the same alphabet
        as self.
        """
        def extended(self, *args, **kwargs):
            return seq_type(Message(s, self.alphabet)
                            for s in getattr(str, method_name)(self, *args, **kwargs))
        return extended

class Message(str, metaclass=MessageMeta):
    """
    A Message is a Python string with an additional attribute which is an
    Alphabet.  The default alphabet is small letters.  

    It is not required that all letters in the message be in the
    alphabet, but those which are not in the alphabet are preserved when
    encrypting the message.  To avoid having them appear in the ciphertext,
    encrypt M.clean() rather than M.

    A Message supports all string methods, but they return Messages with the
    same alphabet, rather than plain strings.
    """
    def __new__(cls, message, alphabet=small):
        return str.__new__(cls, str(message))
    
    def __init__(self, message, alphabet=small):
      if isinstance(message , Message):
          alphabet = message.alphabet
      self.alphabet = alphabet
      self.modulus = len(alphabet)

    def __repr__(self):
        return '*{}*'.format(self)

    def __add__(self, other):
        # Do not allow ambiguity about what the alphabet should be.
        assert isinstance(other, str) or self.alphabet is other.alphabet, \
            'Addition operands must have the same alphabet.'
        return Message(str.__add__(self, other), self.alphabet)

    def __iter__(self):
        for s in str.__iter__(self):
            yield Message(s, self.alphabet)

    def clean(self):
        """
        Return a new message obtained by deleting all letters not in the alphabet.

        >>> m = Message('HELLO, WORLD', big)
        >>> m
        *HELLO, WORLD*
        >>> m.clean()
        *HELLOWORLD*
        """
        result = ''.join(letter for letter in self if letter in self.alphabet)
        return Message(result, self.alphabet)
        
    def substitute(self, substitution):
        """
        Return a message obtained from this one by applying a Substitution.

        >>> m = Message('hello, world', small)
        >>> s1 = Substitution(small, big, lambda n : n + 2)
        >>> m.substitute(s1)
        *JGNNQ, YQTNF*
        """
        result = ''.join(substitution(letter) for letter in self)
        return Message(result, substitution.range)

    def cycle_substitute(self, subs_list):
        """
        Given a list of k Substitutions apply the nth Substitution (mod k) to the
        nth letter.

        >>> m = Message('hello, world', small)
        >>> s1 = Substitution(small, big, lambda n : n + 2)
        >>> m.substitute(s1)
        *JGNNQ, YQTNF*
        >>> s2 = Substitution(small, big, lambda n : n + 5)
        >>> m.substitute(s2)
        *MJQQT, BTWQI*
        >>> m.cycle_substitute([s1, s2])
        *JJNQQ, BQWNI*
        """
        alphabets = set(s.range for s in subs_list)
        assert len(alphabets) == 1, \
            'All Substitutions must have the same range for cycle_substitution.'
        alphabet = alphabets.pop()
        sub = cycle(subs_list)
        result = ''.join([next(sub)(letter) if letter in self.alphabet else letter
                          for letter in self])
        return Message(result, alphabet)

    def smoosh(self, n):
        """
        Cleans the message and divides the result into words of equal
        length n (except for the last word, which may be shorter).
       
        >>> m = Message('hello, world')
        >>> m
        *hello, world*
        >>> m.smoosh(3)
        *hel low orl d*
        """
        assert isinstance(n, int) and n > 0, 'The smoosh length must be a positive integer.'
        result = ' '.join(''.join(p[1] for p in g)
                          for k, g in groupby(enumerate(self.clean()), key=lambda p : p[0]//n))
        return Message(result, self.alphabet)

    def frequencies(self, sort=False):
        """
        Return a list of pairs (l, f) where l is a letter of the alphabet and f is the
        frequency at which l appears in this message.  The pairs are sorted by descending
        frequency if the keyword argument sort is True.  Otherwise they are in the order
        of the alphabet.

        >>> m = Message('Hello worlds')
        >>> m.frequencies(sort=True)[:6]
        [('l', 0.3), ('o', 0.2), ('d', 0.1), ('e', 0.1), ('r', 0.1), ('s', 0.1)]
        """
        alphabet = set(self.alphabet)
        total = float(len([x for x in self if x in alphabet]))
        result = [(x, self.count(x)/total) for x in self.alphabet]
        if sort:
            return sorted(result, key=lambda x: x[1], reverse=True)
        else:
            return result
