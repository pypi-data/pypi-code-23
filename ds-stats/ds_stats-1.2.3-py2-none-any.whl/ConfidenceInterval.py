import numpy as np
from ds_stats.NormalDistribution import NormalDistribution
from ds_stats.tDistribution import tDistribution
from ds_stats.ChiSquareDistribution import ChiSquareDistribution

class ConfidenceInterval:

    @staticmethod
    def mean_on_series(series, sigma = None, alpha = 0.05, precision = 4):
        xbar = series.mean()
        stdev = series.std()
        n = series.count()
        isSigmaKnown = False
        if(sigma):
            stdev = sigma
            isSigmaKnown = True
        return ConfidenceInterval.mean(xbar, stdev, n, alpha = alpha, isSigmaKnown = isSigmaKnown, precision = precision)

    @staticmethod
    def mean(xbar, stdev, n, alpha = 0.05, isSigmaKnown = False, precision = 4):

        stderror = stdev/np.sqrt(n)
        if(n >= 30 and isSigmaKnown):
            score = NormalDistribution(0, 1).getZscore(alpha/2, "right")
        elif(n >= 30 and not isSigmaKnown):
            score = NormalDistribution(0, 1).getZscore(alpha/2, "right")
        elif(n < 30 and isSigmaKnown):
            score = NormalDistribution(0, 1).getZscore(alpha/2, "right")
        else:
            score = tDistribution(n-1).getTscore(alpha/2, "right")

        return (round(xbar - score*stderror, precision), round(xbar + score*stderror, precision))

    @staticmethod
    def proportion_on_series(series, alpha = 0.05, precision = 4):
        p = float(series.sum()) / series.count()
        n = series.count()
        return ConfidenceInterval.proportion(p, n, alpha, precision)

    @staticmethod
    def proportion(p, n, alpha = 0.05, precision = 4):

        q = 1 - p
        stderror = np.sqrt(p*q/n)
        prob = alpha/100.0
        score = NormalDistribution(0, 1).getZscore(alpha/2, "right")
        return (round(p - score*stderror, precision), round(p + score*stderror, precision))

    @staticmethod
    def variance_on_series(series, alpha = 0.05, precision = 4):
        var = series.var()
        n = series.count()
        return ConfidenceInterval.variance(var, n, alpha, precision)

    @staticmethod
    def variance(var, n, alpha = 0.05, precision = 4):

        df = n - 1
        chisq1 = ChiSquareDistribution(n - 1).getChi2score(alpha/2, "left")
        chisq2 = ChiSquareDistribution(n - 1).getChi2score(alpha/2, "right")
        low = round((df * var) / chisq2, precision)
        high = round((df * var) / chisq1, precision)
        return (low, high)