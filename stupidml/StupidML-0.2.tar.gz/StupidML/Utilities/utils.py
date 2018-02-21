import numpy as np
from sklearn.utils.extmath import safe_sparse_dot as safedot

class Kernel():

    def gaussian(self, x, x_, **kwargs):
        if kwargs:
            try:
                sigma = kwargs['sigma']
            except KeyError:
                raise ValueError('Must use proper parameters of Gaussian(RBF) kernel')
        else:
            sigma = 30

        gamma = 1 / (2 * np.square(sigma))
        sq_norm = safedot(x, x) + safedot(x_,x_) - (2 * safedot(x, x_))
        n = gamma * sq_norm
        return np.exp(-n)

    def polynomial(self, x, x_, **kwargs):
        if kwargs:
            try:
                c = kwargs['c']
                d = kwargs['d']
            except KeyError:
                raise ValueError('Must use proper arguments for polynomial kernel')
        else:
            c = 1
            d = 2

        n = safedot(x, x_) + c
        return np.power(n, d)

    def sigmoid(self, x, x_, **kwargs):
        if kwargs:
            try :
                alpha = kwargs['alpha']
                c = kwargs['c']
            except KeyError :
                raise ValueError('Must use proper arguments for sigmoid kernel function.')
        else:
            alpha = 1e-10
            c = 0.5

        n = alpha * safedot(x, x_) + c
        return np.tanh(n)

