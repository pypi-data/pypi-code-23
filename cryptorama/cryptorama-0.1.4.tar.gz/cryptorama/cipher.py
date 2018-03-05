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

from .alphabet import Alphabet, Substitution, big, small
from .message import Message
from .data import english
import re

class Cipher:
    """
    Base class for ciphers.
    """
    
    def encrypt(self, plaintext):
        """
        Encrypt 'plaintext' and return 'ciphertext'
        """
        assert isinstance(plaintext, Message), 'Plaintext is not a Message instance'
        # Subclasses override this.

    def decrypt(self, ciphertext):
        """
        Decrypt 'ciphertext and return 'plaintext'.
        """
        assert isinstance(ciphertext, Message), 'Plaintext is not Message instance'
        plaintext=''
        # Subclasses override this.

    @classmethod
    def crack(cls, ciphertext, plain=small):
        """
        Return the key and the plaintext, in the specified alphabet.
        """
        assert isinstance(ciphertext, Message), 'Plaintext is not Message instance'
        # Subclasses override this.

class AffineCipher(Cipher):
    """
    A affine cipher, using the function x -> m*x + b (mod N) where N is the alphabet
    size.

    Instantiate with a plaintext alphabet, a ciphertext alphabet and integers m and b.
    By default, small letters are used for plaintext and big letters for ciphertext.

    >>> m = Message('hello, world')
    >>> C = AffineCipher(m=5, b=3)
    >>> m
    *hello, world*
    >>> M = C.encrypt(m)
    >>> M
    *MXGGV, JVKGS*
    >>> C.decrypt(M)
    *hello, world*
    """
    def __init__(self, m = 1, b = 0, plain=small, cipher=big):
        if cipher is None:
            cipher = plain
        assert isinstance(plain, Alphabet) and isinstance(cipher, Alphabet), \
            'The arguments "plain" and "cipher" must be Alphabets.'
        assert isinstance(m, int) and isinstance(b, int), \
            'The arguments m and b must be integers'
        self.plain, self.cipher, self.m, self.b = plain, cipher, m , b
        self.substitution = Substitution(self.plain, self.cipher,
                                         lambda x : m*x + b)
        gcd, M, n = xgcd(self.m, len(self.plain))
        assert gcd == 1, 'm is not relatively prime to the length of the alphabet'
        self.inverse = Substitution(self.cipher, self.plain,
                                         lambda y : M*(y - b))
        
    def encrypt(self, plaintext):
        """
        Returns encryption of plaintext using this affine cipher.
        """
        assert isinstance(plaintext, Message), 'Plaintext is not a Message instance'
        assert plaintext.alphabet == self.plain, 'Plaintext does not use the right alphabet'
        return plaintext.substitute(self.substitution)

    def decrypt(self, ciphertext):
        """
        Returns decryption of ciphertext that was encrypted with this affine cipher.
        """
        assert isinstance(ciphertext, Message), 'Ciphertext is not a Message instance'
        assert ciphertext.alphabet == self.cipher, 'Ciphertext does not use the right alphabet'
        return ciphertext.substitute(self.inverse)

class CaesarCipher(AffineCipher):
    """
    A Ceasar cipher is an affine cipher with m = 1.  The key, b, can be provided as a
    letter in the ciphertext alphabet or an integer.

    >>> C = CaesarCipher(key='M')
    >>> m = Message('hello, world')
    >>> m
    *hello, world*
    >>> M = C.encrypt(m)
    >>> M
    *TQXXA, IADXP*
    >>> C.decrypt(M)
    *hello, world*
    """
    
    def __init__(self, key=0, plain=small, cipher=big):
        self.key = key
        if isinstance(key, int):
            AffineCipher.__init__(self, m=1, b=key, plain=plain, cipher=cipher)
        else:
            AffineCipher.__init__(self, plain=plain, cipher=cipher, m=1, b=cipher(key))

    @classmethod
    def crack(cls, ciphertext, plain=small):
        """
        Brute force. Returns a dictionary mapping each key to the message obtained by
        decrypting with that key.

        >>> m = Message('hello, world')
        >>> m
        *hello, world*
        >>> C = CaesarCipher(key='F')
        >>> M = C.encrypt(m)
        >>> M
        *MJQQT, BTWQI*
        >>> tries = CaesarCipher.crack(M)
        >>> tries['B']
        *lipps, asvph*
        >>> tries['F']
        *hello, world*
        """
        assert len(plain) == len(ciphertext.alphabet), 'Plaintext alphabet has the wrong size.'
        result = {}
        for letter in ciphertext.alphabet:
            cipher = CaesarCipher(letter, plain, ciphertext.alphabet)
            result[letter] = cipher.decrypt(ciphertext)
        return result

class SubstitutionCipher(Cipher):
    """
    Maps the plaintext alphabet to the ciphertext alphabet by an arbitrary
    bijection.  The bijection is the composition of the order preserving
    bijection between the two alphabets followed by a permutation of the
    ciphertext alphabet.  The permutation is specified as a keyword which is a
    sequence of letters in the ciphertext alphabet.  When constructing a
    SubstitutionCipher, pass the keyword as the unique positional argument.

    >>> m = Message('hello, world')
    >>> m
    *hello, world*
    >>> qwerty = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    >>> S = SubstitutionCipher(qwerty)
    >>> M = S.encrypt(m)
    >>> M
    *ITSSG, VGKSR*
    >>> M.alphabet
    ABCDEFGHIJKLMNOPQRSTUVWXYZ
    >>> S.decrypt(M)
    *hello, world*
    """

    def __init__(self, keyword, plain=small, cipher=big):
        assert isinstance(plain, Alphabet) and isinstance(cipher, Alphabet), \
            'The arguments "plain" and "cipher" must be Alphabets.'
        assert len(keyword) == len(cipher) and set(keyword) == set(cipher), \
            'Keyword does not define a bijection'
        self.plain, self.cipher = plain, cipher
        self.substitution = Substitution(plain, cipher, lambda x: cipher(keyword[x]))
        self.inverse_dict = dict((cipher(keyword[n]), n) for n in range(len(plain)))
        self.inverse = Substitution(cipher, plain, lambda y: self.inverse_dict[y])

    def encrypt(self, plaintext):
        """
        Returns encryption of plaintext.
        """
        assert isinstance(plaintext, Message), 'Plaintext is not a Message instance'
        assert plaintext.alphabet == self.plain, 'Plaintext does not use the right alphabet'
        return plaintext.substitute(self.substitution)

    def decrypt(self, ciphertext):
        """
        Returns decryption of ciphertext.
        """
        assert isinstance(ciphertext, Message), 'Ciphertext is not a Message instance'
        assert ciphertext.alphabet == self.cipher, 'Ciphertext does not use the right alphabet'
        return ciphertext.substitute(self.inverse)

class KeywordCipher(SubstitutionCipher):
    """
    A substitution cipher where the keyword is obtained by removing
    duplicate letters from the keyword concatenated with the
    ciphertext alphabet, then shifting by the index of the keyletter.
    the keyword and keyletter must consist of letters from the
    ciphertext alphabet.

    >>> c = KeywordCipher('BANANA', 'g')
    >>> c.cipher
    ABCDEFGHIJKLMNOPQRSTUVWXYZ
    >>> c.encrypt(Message(small))
    *UVWXYZBANCDEFGHIJKLMOPQRST*
    >>> M = c.encrypt(Message('hello world'))
    >>> M
    *AYEEH QHKEX*
    >>> c.decrypt(M)
    *hello world*
    """
    
    def __init__(self, keyword, keyletter, plain=small, cipher=big):
        cipher_string = str(cipher)
        assert re.search('[^%s]'%cipher, keyword) is None, \
            'The keyword must consist of letters in the ciphertext alphabet'
        assert keyletter in plain, 'The keyletter must be in the plaintext alpabet'
        head, sep, tail = str(cipher).partition(cipher[plain(keyletter)])
        assert sep != '', 'Key letter is not in the alphabet.'
        n = len(head)
        permutation = self._undup(keyword + cipher_string)
        permutation = permutation[-n:] + permutation[:-n]
        return SubstitutionCipher.__init__(self, permutation, plain, cipher)

    def _undup(self, x):
        n = 0
        while len(x) > n:
            x = x[:n + 1] + re.sub(x[n], '', x[n+1:])
            n += 1
        return x
    
class MultiplicativeCipher(AffineCipher):
    """
    A MultiplicativeCipher is an affine cipher with b=0.

    >>> m = Message('hello, world')
    >>> m
    *hello, world*
    >>> C = MultiplicativeCipher(key=5)
    >>> M = C.encrypt(m)
    >>> M
    *JUDDS, GSHDP*
    >>> C.decrypt(M)
    *hello, world*
    """
    
    def __init__(self, key=1, plain=small, cipher=big):
        self.key = key
        AffineCipher.__init__(self, plain=plain, cipher=cipher, m=key, b=0)

class VigenereCipher(Cipher):
    """
    The Vigenere cipher uses a cycle substitution where the nth substitution in
    the cycle is a shift by the nth letter of the key word.

    >>> m = Message('hello, world')
    >>> m
    *hello, world*
    >>> V = VigenereCipher(keyword='BYE')
    >>> M = V.encrypt(m)
    >>> M
    *ICPMM, APPPE*
    >>> V.decrypt(M)
    *hello, world*
    """

    def __init__(self, keyword='', plain=small, cipher=big):
        self.keyword, self.plain, self.cipher = keyword, plain, cipher
        assert len(plain) == len(cipher), 'Alphabets must be the same size'
        def shift(letter):
            n = cipher(letter)
            return lambda x : x + n
        self.substitutions = [Substitution(plain, cipher, shift(letter))
                              for letter in keyword]
        def inverse(letter):
            n = cipher(letter)
            return lambda x : x - n
        self.inverses = [Substitution(cipher, plain, inverse(letter))
                             for letter in keyword]

    def encrypt(self, plaintext):
        """
        Returns encryption of plaintext using this affine cipher.
        """
        assert isinstance(plaintext, Message), 'Plaintext is not a Message instance'
        assert plaintext.alphabet == self.plain, 'Plaintext does not use the right alphabet'
        return plaintext.cycle_substitute(self.substitutions)

    def decrypt(self, ciphertext):
        """
        Returns decryption of ciphertext that was encrypted with this affine cipher.
        """
        assert isinstance(ciphertext, Message), 'Ciphertext is not a Message instance'
        assert ciphertext.alphabet == self.cipher, 'Ciphertext does not use the right alphabet'
        return ciphertext.cycle_substitute(self.inverses)

    @classmethod
    def crack(cls, ciphertext, plain=small):
        """
        Crack a Vigenere cipher by using Bonnie's algorithm.

        >>> M = Message('YBRWY JFM N QCGYFR GIL SUZJX WJMFJ. NUJ VVL VBDM VS NUJ HRNAUGIEMIBI WBSMGFHGQS GJUFJX UNG. FTGRYCZJM GMYL TZSJLRI BVR U PMIVHY OJNJJYA F HVHERQ UAI U QNGR. OYFXY NQQNDM GTIX YBR SCPPYY-FZGJL NQF, VY QNX VVLARW. NUJ VVL VBDM YFOTMYQ FHQ QUHLBRI. IAJ XND USYYE OYFXY TWUOGYQ YBR SCPPYY, MCF KUGMYE YIBP BVR UFNXR FHQ XUVI, "DRXMR, YBBXY OTSF FLR RUXNHT KOA TZ LTO. GMYL YBVSE LTO QTHG PHBB NUJ XVRY VX QBWNU RIEJ NUFH GMY ANWXJF." WJMFJ AENHAJX NSX FFCQ, "IIAY QBWLL IUQ. N EATQ JMCPM CF BIEYB ZTLR. GOG NZ V YIBP NUJ XVRY, GMYL BIHQX FYIC IIVSA VY. MB KUE NPR HIYQYPYYQ $10 IIYQUEX."', big)
        >>> VigenereCipher.crack(M)
        ('FUN', *there was a little boy named jesse. the big boys in the neighborhood constantly teased him. sometimes they offered him a choice between a nickel and a dime. jesse always took the nickel-after all, it was bigger. the big boys laughed and laughed. one day after jesse grabbed the nickel, his father took him aside and said, "jesse, those boys are making fun of you. they think you dont know the dime is worth more than the nickel." jesse grinned and said, "dont worry dad. i know which is worth more. but if i took the dime, they would stop doing it. so far ive collected $10 dollars."*)
        """
        assert len(plain) == len(ciphertext.alphabet), 'Plaintext alphabet has the wrong size.'
        E = ciphertext.clean()
        # Assume the keyword has length at most 20.
        maxshift = 20
        # Guess the keyword length as the shift amount which gives the most matches.
        shift_matches = cls._shift_matches(E, maxshift)[3:]
        keylength = shift_matches.index(max(shift_matches)) + 3
        # Look at substrings with stride equal to keylength.  Each of these would have
        # been shifted by the same amount when the message was encrypted.
        substrings = [E[n:len(E):keylength] for n in range(keylength)]
        # Analize their frequencies to find the most likely shift for each substring.
        # (This is a weak spot: if a multiple of the real keylength is used then the data per
        # substring is less and therefore the analysis is less accurate.)
        substring_freqs = [substrings[i].frequencies() for i in range(keylength)]
        keyword = cls._find_keyword(E, keylength, substrings, substring_freqs)
        # Decrypt.
        plaintext = cls(keyword, plain, ciphertext.alphabet).decrypt(ciphertext)
        return keyword, plaintext

    @staticmethod
    def _shift_matches(message, maxshift=20):
        """
        Return the number of matches of the message with each shift up to maxshift.
        """
        l = len(message)
        matches = [0]
        for shift in range(1, maxshift):
            matches.append(len([ x for x in range(l-shift) if message[x+shift]==message[x] ]))
        return matches

    @staticmethod
    def _find_keyword(message, keylength, substrings, substring_freqs):
        keyword=''
        cipher = message.alphabet
        m = len(cipher)
        def correlation(freqs, j):
            """
            Correlation between a shifted frequency distribution and the frequency
            distribution of English.
            """
            return sum([freqs[(i+j) % m][1]*english[i][1] for i in range(m)])
        # Build up the keyword.
        for i in range(keylength):
            # Which shift has frequencies closest to the frequencies of English?
            correlations = [(j, correlation(substring_freqs[i], j)) for j in range(m)]
            correlations.sort(key = lambda x: x[1], reverse=True)
            # Add that shift to the keyword.
            keyword += cipher[correlations[0][0]]
        # Check for periodicity in the keyword and reduce accordingly.        
        for factor in [n for n in range(3, keylength) if keylength % n == 0]: 
            prefix = keyword[:factor]
            if keyword == prefix*(keylength//factor):
                keyword = prefix
                break
        return keyword

def xgcd(A,B):
    """
    Finds g=gcd(A,B) and solves the equation A*n+B*m=gcd(A,B).  Returns g, n, m.
    """
    a, b = A, B
    n1, m1, n, m = 0, 1, 1, 0
    if B == 0:
      return A, 1, 0
    r = b
    while r > 0:
        g = r
        q, r = divmod(a,b)
        n1, m1, n, m = n-q*n1, m-q*m1, n1, m1
        a, b = b, r       
        # A*n1 + B*m1 = r, last time will be r = 0, so A*n + B*m = g. 
    return g, n, m
