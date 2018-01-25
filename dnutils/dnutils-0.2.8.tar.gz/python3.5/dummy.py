from dnutils import out
from dnutils.stats import Gaussian

g1 = Gaussian(mean=[0, 0], cov=[[1, 0], [0, 1]])
g2 = Gaussian(mean=[.1, .01], cov=[[1, .1], [.1, 1]])

if __name__ == '__main__':
    out(g1.kldiv(g2))
