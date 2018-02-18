import scipy.stats
import numpy as np
import numpy.random
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

class tDistribution:

    def __init__(self, df, mean = 0, sd = 1,precision = 4):

        self.df = df
        self.mean = mean
        self.sd = sd
        self.precision = precision

    def getProbability(self, low, high):

        tObj = self.__getStatsObj()
        prob = tObj.cdf(high) - tObj.cdf(low)
        return round(prob, self.precision)

    def getLeftProbability(self, x):

        tObj = self.__getStatsObj()
        prob = tObj.cdf(x)
        return round(prob, self.precision)

    def getRightProbability(self, x):

        leftProb = self.getLeftProbability(x)
        rightProb = 1 - leftProb
        return round(rightProb, self.precision)

    def getRandomNumbers(self, n):

        tObj = self.__getStatsObj()
        return tObj.rvs(n)

    def getTscore(self, alpha, side):

        prob = alpha
        if(side == "left"):
            prob = alpha
        elif(side == "right"):
            prob = 1 - alpha
        else:
            raise ValueError("Side should be either of left, right")
        tObj = self.__getStatsObj()
        tScore = tObj.ppf(prob)
        return round(tScore, self.precision)

    def plot(self):

        tObj = self.__getStatsObj()

        x = np.linspace(self.mean - 3*self.sd, self.mean + 3*self.sd, 100)
        y = [tObj.pdf(i) for i in x]
        scatterData = [go.Scatter(x = x, y = y,mode = 'lines')]
        plotly.offline.init_notebook_mode()
        plotly.offline.iplot(scatterData, filename='jupyter/Normal')

    def __getStatsObj(self):

        tObj = scipy.stats.t(self.df, loc = self.mean, scale = self.sd)
        return tObj

    def getMean(self):

        return round(self.mean, self.precision)

    def getVariance(self):

        return round(self.sd ** 2, self.precision)

    def getStandardDev(self):

        return round(self.sd, self.precision)