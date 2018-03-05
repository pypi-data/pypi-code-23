import sys
if sys.version_info.major != 3 or sys.version_info.minor < 5:
    raise RuntimeError('Please use Python 3.5 or newer.')
    
from .cipher import (CaesarCipher, MultiplicativeCipher, AffineCipher, SubstitutionCipher,
                     KeywordCipher, VigenereCipher)
from .message import Message
from .alphabet import Alphabet, Substitution, big, small, upper, lower
from .version import __version__
