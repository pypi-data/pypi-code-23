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

from collections import OrderedDict

class Alphabet(OrderedDict):
    """
    A bijection from Z/nZ to a set of letters.  The
    letters are strings of length 1.  An alphabet is initialized with
    a string of length n.  If this initialization string has repeated
    letters a ValueError is raised.

    Use [] to map from indexes to letters.  Use () to map from letters to
    indexes.
    """
    
    def __init__(self, letters):
        assert isinstance(letters, str), 'Letters must be strings'
        super(Alphabet, self).__init__((letter, m) for m, letter in enumerate(letters))
        if len(self) != len(letters):
            raise ValueError('Repeated letters are not allowed.')
        self.letters = letters
        self.modulus = len(letters)
        self._map = dict(enumerate(letters))
        self._hash = hash(letters)

    def __call__(self, letter):
        return self.get(letter, None)

    def __getitem__(self, index):
        return self._map.get(index % self.modulus, None)

    def __repr__(self):
        return self.letters

    def __hash__(self):
        return self._hash


class Substitution:
    """
    A bijection from one alphabet to another, defined by a python function that is
    assumed to give a bijection between the index rings of the two alphabets.
    On letters not in the domain alphabet, a Substitution acts as the identity.
    
    For alphabets A and B and a function f, the mapping is A[m] -> B[f(m)].
    """
    def __init__(self, domain, range, function):
        assert len(domain) == len(range), 'The alphabets must be the same size.'
        self.domain, self.range, self.function = domain, range, function

    def __call__(self, letter):
        if letter in self.domain:
            return self.range[self.function(self.domain(letter))]
        else:
            return letter

big = caps = upper = Alphabet('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
small = little = lower = Alphabet('abcdefghijklmnopqrstuvwxyz')

