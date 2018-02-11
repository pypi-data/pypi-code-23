import scipy.stats
import numpy as np
import numpy.random
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
class FDistribution:

    def __init__(self, df1, df2, precision = 4):
        self.df1 = df1
        self.df2 = df2
        self.precision = precision

    def getProbability(self, low, high):
        fDistObj = self.__getStatsObj()
        prob = fDistObj.cdf(high) - fDistObj.cdf(low)
        return round(prob, self.precision)

    def getLeftProbability(self, x):
        fDistObj = self.__getStatsObj()
        prob = fDistObj.cdf(x)
        return round(prob, self.precision)

    def getRightProbability(self, x):
        leftProb = self.getLeftProbability(x)
        rightProb = 1 - leftProb
        return round(rightProb, self.precision)

    def getRandomNumbers(self, n):
        fDistObj = self.__getStatsObj()
        return fDistObj.rvs(n)

    def getFscore(self, probability):
        fDistObj = self.__getStatsObj()
        prob = fDistObj.ppf(probability)
        return round(prob, self.precision)

    def plot(self):
        fDistObj = self.__getStatsObj()

        x = np.linspace(0, 50, 100)
        y = [fDistObj.pdf(i) for i in x]
        scatterData = [go.Scatter(x = x, y = y,mode = 'lines')]
        plotly.offline.init_notebook_mode()
        plotly.offline.iplot(scatterData, filename='jupyter/FDist')
    def getStatsObj(self):
        return self.__getStatsObj()
    def __getStatsObj(self):
        fDistObj = scipy.stats.f(self.df1, self.df2)
        return fDistObj

    def getMean(self):
        fDistObj = self.__getStatsObj()
        return round(fDistObj.mean(), self.precision)

    def getVariance(self):
        fDistObj = self.__getStatsObj()
        return round(fDistObj.var(), self.precision)

    def getStandardDev(self):
        fDistObj = self.__getStatsObj()
        return round(fDistObj.std(), self.precision)