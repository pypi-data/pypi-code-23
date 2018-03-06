from theano import tensor as T
from theano.tensor import fft


def rfft(x):
    """x: batch of data (TODO: check it out)"""
    return fft.rfft(x)
    

if __name__ == '__main__':
    N = 32

    pass