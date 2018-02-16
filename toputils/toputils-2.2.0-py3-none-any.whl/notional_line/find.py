import math

import scipy.optimize

def finder(line, prob, dist, **kwargs):
    """ Accepts a distribution, line and probability of that line
    and returns the 50/50 probability line.
    

    :param line: the known line.
    :param prob: the probability of the known line.
    :param dist: scipy.stats object or some other dist object that
        has a .cdf() method.
    :param kwargs: keyword arguments passed to .cdf() function of 
        dist.
    
    """
    
    test_line = float(line)
    
    def func(test_line):
        return prob - dist.cdf(line, test_line, **kwargs)
        
    return scipy.optimize.fsolve(func, test_line)
