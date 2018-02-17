__version__ = '1.0.0'


class Base62():
    """
    Encoder and decoder for Base62 integers.
    """
    def __init__(self):
        self.charset = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                       'abcdefghijklmnopqrstuvwxyz'

    def encode(self, number):
        """
        Encode a number to base62 format.
        :param number:
        :return:
        >>> b = Base62()
        >>> b.encode(34441886726)
        'base62'
        >>> b.encode(1337)
        'LZ'
        """
        if number == 0:
            return '0'
        s = list()
        while number > 0:
            n = number % 62
            s.append(self.charset[n])
            number //= 62
        s.reverse()
        return ''.join(s)

    def decode(self, text):
        """
        Decode a base62 string to an integer.
        :param text:
        :return:
        >>> b = Base62()
        >>> b.decode("base62")
        34441886726
        >>> b.decode('LZ')
        1337
        """
        result = 0
        for i in range(0, len(text)):
            result += self.charset.index(text[i]) * 62 ** (len(text) - 1 - i)
        return result
