'''
Auxiliar mathematical functions.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Custom
from hep_spt.core import decorate

# Python
import numpy as np
from functools import reduce


__all__ = ['gcd', 'is_power_2', 'lcm', 'next_power_2']


@decorate(np.vectorize)
def gcd( a, b, *args ):
    '''
    :param a: first number.
    :type a: int
    :param b: second number.
    :type b: int
    :param args: any other numbers.
    :type args: collection(int)
    :returns: greatest common divisor of "a" and "b".
    :rtype: int
    '''
    if len(args) == 0:
        while b:
            a, b = b, a % b
        return a
    else:
        return reduce(gcd, args + (a, b))


@decorate(np.vectorize)
def is_power_2( n ):
    '''
    :param n: input number.
    :type n: int
    :returns: whether the input number is a power of 2 or not.
    :rtype: bool
    '''
    return n > 0 and ((n & (n - 1)) == 0)


@decorate(np.vectorize)
def lcm( a, b, *args ):
    '''
    :param a: first number.
    :type a: int
    :param b: second number.
    :type b: int
    :param args: any other numbers.
    :type args: collection(int)
    :returns: least common multiple of "a" and "b".
    :rtype: int
    '''
    if len(args) == 0:
        return a*b//gcd(a, b)
    else:
        return reduce(lcm, args + (a, b))


@decorate(np.vectorize)
def next_power_2( n ):
    '''
    :param n: input number.
    :type n: int
    :returns: next power of 2 to the given number.
    :rtype: int

    .. note: If the input number is a power of two, it will return the \
    same number.
    '''
    return 1 << int(n - 1).bit_length()
