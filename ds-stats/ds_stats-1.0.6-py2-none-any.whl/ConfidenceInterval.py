import numpy as np
from NormalDistribution import NormalDistribution
from tDistribution import tDistribution
from ChiSquareDistribution import ChiSquareDistribution

class ConfidenceInterval:

    @staticmethod
    def mean(xbar, stdev, n, alpha = 5, isSigmaKnown = True, precision = 4):

        stderror = stdev/np.sqrt(n)
        p = alpha / 100.0
        if(n >= 30 and isSigmaKnown):
            score = NormalDistribution(0, 1).getZscore(1 - p/2.0)
        elif(n >= 30 and not isSigmaKnown):
            score = NormalDistribution(0, 1).getZscore(1 - p/2.0)
        elif(n < 30 and isSigmaKnown):
            score = NormalDistribution(0, 1).getZscore(1 - p/2.0)
        else:
            score = tDistribution(n-1).getTscore(1 - p/2.0)

        return (round(xbar - score*stderror, precision), round(xbar + score*stderror, precision))

    @staticmethod
    def proportion(p, n, alpha = 5, precision = 4):

        q = 1 - p
        stderror = np.sqrt(p*q/n)
        prob = alpha/100.0
        score = NormalDistribution(0, 1).getZscore(1 - prob / 2.0)
        return (round(p - score*stderror, precision), round(p + score*stderror, precision))

    @staticmethod
    def variance(n, stdev, alpha = 5, precision = 4):

        p = alpha / 100.0
        df = n - 1
        chisq1 = ChiSquareDistribution(n - 1).getChi2score(1 - p / 2.0)
        chisq2 = ChiSquareDistribution(n - 1).getChi2score(p / 2.0)
        low = round(df * (stdev**2) / chisq1, precision)
        high = round(df * (stdev**2) / chisq2, precision)
        return (low, high)