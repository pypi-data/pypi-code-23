from scipy.stats import poisson
import pandas as pd
import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

class PoissonDistribution:
    def __init__(self, n, p):
        self.n = n
        self.p = p
        self.mu = n * p
        self.poissonObj = self.__getStatsObj()

    def exactProbability(self, k, precision = 4):
        prob = self.poissonObj.pmf(k)
        return round(prob, precision)

    def atleastProbability(self, k, precision = 4):
        lst = [self.poissonObj.pmf(k) for i in range(k, self.n+1)]
        prob = sum(lst)
        return round(prob, precision)

    def atmostProbability(self, k, precision = 4):
        lst = [self.poissonObj.pmf(k) for i in range(0, k+1)]
        prob = sum(lst)
        return round(prob, precision)

    def generateTable(self, precision = 4):
        exactProbs = np.array([self.exactProbability(i, precision) for i in range(0, self.n + 1)])
        atleastProbs = np.array([self.atleastProbability(i, precision) for i in range(0, self.n + 1)])
        atmostProbs = np.array([self.atmostProbability(i, precision) for i in range(0, self.n + 1)])
        return pd.DataFrame({'P(Exactly k)': exactProbs, 'P(Atleast k)': atleastProbs, 'P(Atmost k)': atmostProbs}).rename_axis('k', axis="columns")

    def getRandomNumbers(self, n):
        return self.poissonObj.rvs(n)

    def __getStatsObj(self):
        poissonObj = poisson(self.mu)
        return poissonObj

    def plot(self, precision = 4):
        x = range(0, self.n + 1)
        y = [self.exactProbability(i, precision) for i in range(0, self.n + 1)]
        data = [go.Bar(x=x, y=y)]
        plotly.offline.init_notebook_mode()
        plotly.offline.iplot(data, filename='jupyter/barchart')

    def getMean(self, precision = 4):
        return round(self.poissonObj.mean(), precision)

    def getVariance(self, precision = 4):
        return round(self.poissonObj.var(), precision)

    def getStandardDev(self, precision = 4):
        return round(self.poissonObj.std(), precision)