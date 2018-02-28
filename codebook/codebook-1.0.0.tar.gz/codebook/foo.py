# import numpy as np

aaa = 42
bbb = 442
ccc = 422


def foo(a=1, b=2):
    """A function"""
    bar(88, 99)

def bar(c=3, d=4):
    """A function"""
    x = 5
    raise Exception

def biz(e=5, f=6):
    """A function

    >>> e = 77
    >>> f = 88

    """
    g = e + f
    return g

def baz(h, i=7):
    """A function

    >>> h = 8

    """
    j = h + i
    return j


if __name__ == '__main__':
    import IPython
    IPython.embed_kernel()
