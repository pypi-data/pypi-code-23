"""

A small collection of functions.

"""


def foo(a=1, b=2):
    c = a + b
    return c


def bar(d=3, e=4):
    import os
    try:
        pid = os.fork()
    except OSError:
        exit(1)
    if pid > 0:
        exit(0)
    import IPython
    IPython.embed_kernel()


if __name__ == '__main__':
    bar()
