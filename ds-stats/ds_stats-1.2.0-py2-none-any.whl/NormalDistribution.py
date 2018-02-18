import scipy.stats
import numpy as np
import plotly
import plotly.graph_objs as go
class NormalDistribution:

    def __init__(self, mean = 0, sd = 1, precision = 4):
        self.mean = mean
        self.sd = sd
        self.precision = precision
        self.normObj = self.__getStatsObj()

    def getProbability(self, low, high):
        normObj = self.normObj
        prob = normObj.cdf(high) - normObj.cdf(low)
        return round(prob, self.precision)

    def getLeftProbability(self, x):
        normObj = self.normObj
        prob = normObj.cdf(x)
        return round(prob, self.precision)

    def getRightProbability(self, x):
        leftProb = self.getLeftProbability(x)
        rightProb = 1 - leftProb
        return round(rightProb, self.precision)

    def getRandomNumbers(self, n):
        normObj = self.normObj
        return normObj.rvs(n)

    def getZscore(self, alpha, side):
        prob = alpha
        if(side == "left"):
            prob = alpha
        elif(side == "right"):
            prob = 1 - alpha
        else:
            raise ValueError("Side should be either of left, right")
        zscore = scipy.stats.norm.ppf(prob, loc = self.mean, scale = self.sd)
        return round(zscore, self.precision)

    def plot(self):
        normObj = self.normObj

        x = np.linspace(self.mean - 3*self.sd, self.mean + 3*self.sd, 100)
        y = [normObj.pdf(i) for i in x]
        scatterData = [go.Scatter(x = x, y = y,mode = 'lines')]
        plotly.offline.init_notebook_mode()
        plotly.offline.iplot(scatterData, filename='jupyter/Normal')

    def __getStatsObj(self):
        tObj = scipy.stats.norm(self.mean, self.sd)
        return tObj

    def getMean(self):
        return round(self.mean, self.precision)

    def getVariance(self):
        return round(self.sd ** 2, self.precision)

    def getStandardDev(self):
        return round(self.sd, self.precision)