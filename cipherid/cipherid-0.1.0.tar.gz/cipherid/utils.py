import math
from functools import reduce


def mix_alphabet(_string, salt):
    if not salt:
        return _string
    new_sequence = [''] * len(_string)
    left_indexes = list(range(len(_string)))
    for index, s in enumerate(_string):
        l = ord(s) * reduce(lambda acc, x: acc * math.log(ord(x), 10), salt[index::(ord(s) % 3) + 1], 1)
        index_num = round(l % len(salt)) % len(left_indexes)
        i = left_indexes.pop(index_num)
        new_sequence[i] = s
    return ''.join(new_sequence)
