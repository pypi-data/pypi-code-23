import scipy.stats
import numpy as np
import numpy.random
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
class ChiSquareDistribution:

    def __init__(self, df, precision = 4):
        self.df = df
        self.precision = precision

    def getProbability(self, low, high):
        chi2Obj = self.__getStatsObj()
        prob = chi2Obj.cdf(high) - chi2Obj.cdf(low)
        return round(prob, self.precision)

    def getLeftProbability(self, x):
        chi2Obj = self.__getStatsObj()
        prob = chi2Obj.cdf(x)
        return round(prob, self.precision)

    def getRightProbability(self, x):
        leftProb = self.getLeftProbability(x)
        rightProb = 1 - leftProb
        return round(rightProb, self.precision)

    def getRandomNumbers(self, n):
        chi2Obj = self.__getStatsObj()
        return chi2Obj.rvs(n)

    def getChi2score(self, alpha, side):
        prob = alpha
        if(side == "left"):
            prob = alpha
        elif(side == "right"):
            prob = 1 - alpha
        else:
            raise ValueError("Side should be either of left, right")
        chi2Obj = self.__getStatsObj()
        chi2Score = chi2Obj.ppf(prob)
        return round(chi2Score, self.precision)

    def plot(self, n = 50):
        chi2Obj = self.__getStatsObj()

        x = np.linspace(0, n, n * 2)
        y = [chi2Obj.pdf(i) for i in x]
        scatterData = [go.Scatter(x = x, y = y,mode = 'lines')]
        plotly.offline.init_notebook_mode()
        plotly.offline.iplot(scatterData, filename='jupyter/Normal')

    def __getStatsObj(self):
        chi2Obj = scipy.stats.chi2(self.df)

        return chi2Obj

    def getMean(self):
        chi2Obj = self.__getStatsObj()
        return round(chi2Obj.mean(), self.precision)

    def getVariance(self):
        chi2Obj = self.__getStatsObj()
        return round(chi2Obj.var(), self.precision)

    def getStandardDev(self):
        chi2Obj = self.__getStatsObj()
        return round(chi2Obj.std(), self.precision)