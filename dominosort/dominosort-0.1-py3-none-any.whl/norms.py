import numpy as np


def Norm(x):
    raise NotImplementedError('Unspecific norm')


def L1Norm(x):
    return np.sum(np.abs(x))


def L2Norm(x):
    return np.sqrt(np.dot(x, x))
