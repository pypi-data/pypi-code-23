from operator import add
import numpy as np
import numpy.random as random
from scipy.stats import weibull_min, kstest
from tdigest import TDigest

np.random.seed(100)

c = 1
N = 10000
dist = weibull_min(c)

n_monoids_to_add = [5, 25, 50, 100]
data = {}


def add_sample_values_from_dist(tdigest, sample_size):
    tdigest.batch_update(dist.rvs(sample_size))
    return tdigest

for n in n_monoids_to_add:
    sample_size = N / n
    ks_tests = []
    for _ in xrange(5):
        t_sum = reduce(add, (add_sample_values_from_dist(TDigest(delta=0.1, K=15), sample_size) for _ in xrange(n)))
        rvs = np.array([t_sum.percentile(100*random.random()) for _ in xrange(1000)])
        ks_tests.append(kstest(rvs, 'weibull_min', args=(c,)).statistic)
    data[n] = (np.mean(ks_tests), np.var(ks_tests))



for (_, v) in sorted(data.items()):
    print _, v[0], v[1]