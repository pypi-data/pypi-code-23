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

import sys
from doctest import testmod
from . import alphabet, message, cipher

def test():
    for module in (alphabet, message, cipher):
        if '-v' in sys.argv or '--verbose' in sys.argv:
            testmod(module, verbose=True)
        else:
            testmod(module)

if __name__ == '__main__':
    test()
