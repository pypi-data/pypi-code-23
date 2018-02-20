import math
from string import digits, ascii_lowercase, ascii_uppercase

from cipherid.utils import mix_alphabet


DIGITS = digits + ascii_lowercase + ascii_uppercase
BASE = len(DIGITS)


class BaseCoder:
    def __init__(self, salt, base=None, alphabet=None, min_length=0):
        alphabet = alphabet if alphabet else DIGITS
        base = base if base else BASE
        if len(alphabet) < base:
            raise ValueError(f'Too small alphabet for base{base}: {alphabet}')
        self.salt = salt
        self.alphabet = mix_alphabet(alphabet, salt)
        self.base = base
        self.min_length = min_length

    def _ensure_min_length(self, coded):
        len_diff = self.min_length - len(coded)
        if self.min_length and len_diff > 0:
            return f'{self.alphabet[0] * len_diff}{coded}'
        return coded

    def _get_shifted_char(self, step, old_char):
        new_index = (step + self.alphabet.index(old_char)) % len(self.alphabet)
        return self.alphabet[new_index]

    def _get_unshifted_char(self, step, new_char):
        old_index = (self.alphabet.index(new_char) - step) % len(self.alphabet)
        return self.alphabet[old_index]

    def _reorder_encoded(self, encoded, get_char_rule, direct_order=True):
        base_shift_step = self.alphabet.index(encoded[-1])
        previous_shifted_char = encoded[-1]
        reordered = [encoded[-1]]
        for s in reversed(encoded[:-1]):
            shift_step = base_shift_step + self.alphabet.index(previous_shifted_char)
            previous_shifted_char = get_char_rule(shift_step, s) if direct_order else s
            reordered.append(get_char_rule(shift_step, s))
        return ''.join(reversed(reordered))

    def _shift(self, encoded):
        return self._reorder_encoded(encoded, self._get_shifted_char)

    def _unshift(self, encoded):
        return self._reorder_encoded(encoded, self._get_unshifted_char, direct_order=False)

    def _strip(self, coded):
        return coded.lstrip(self.alphabet[0])

    def to_base(self, num):
        """
        Converts integer number to appropriate base.

        :param num: integer > 0
        :return: string that represent `num' in appropriate base

        Examples for salt "My awesome salt"
        >>> e = BaseCoder("My awesome salt")

        >>> e.to_base(1)
        '3'
        >>> e.to_base(3845)
        'i03'
        >>> e.to_base(38415455)
        'ZPjP1'
        >>> e.to_base(38415456)
        'iQ4Xj'
        """
        if not (isinstance(num, int) and num > 0):
            raise ValueError(
                f'Possible to encode only positive integers. Got {type(num)}({num})'
            )

        def get_chars(n):
            while n > 0:
                yield self.alphabet[n % self.base]
                n //= self.base

        return self._shift(self._ensure_min_length(
            ''.join(reversed(list(get_chars(num))))))

    def from_base(self, num_str):
        """
        Converts string that represent a number in appropriate base to integer in base 10.

        :param num_str: string that represent a number in appropriate base
        :return: integer in base 10

        Examples for salt "My awesome salt"
        >>> e = BaseCoder("My awesome salt")

        >>> e.from_base('3')
        1
        >>> e.from_base('i03')
        3845
        >>> e.from_base('ZPjP1')
        38415455
        >>> e.from_base('iQ4Xj')
        38415456
        """
        return sum(
            int(math.pow(self.base, idx)) * self.alphabet.index(char)
            for idx, char in enumerate(reversed(self._strip(self._unshift(num_str))))
        )
