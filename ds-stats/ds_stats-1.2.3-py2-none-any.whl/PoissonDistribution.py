from scipy.stats import poisson
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go

class PoissonDistribution:
    def __init__(self, mu, precision = 4):

        self.mu = mu
        self.poissonObj = self.__getStatsObj()
        self.precision = precision

    def exactProbability(self, k):
        prob = self.poissonObj.pmf(k)
        return round(prob, self.precision)

    def atleastProbability(self, k, n = 10):
        lst = [self.poissonObj.pmf(i) for i in range(k, n+1)]
        prob = sum(lst)
        return round(prob, self.precision)

    def atmostProbability(self, k):
        lst = [self.poissonObj.pmf(i) for i in range(0, k+1)]
        prob = sum(lst)
        return round(prob, self.precision)

    def generateTable(self, n = 10):
        exactProbs = np.array([self.exactProbability(i) for i in range(0, n + 1)])
        atleastProbs = np.array([self.atleastProbability(i) for i in range(0, n + 1)])
        atmostProbs = np.array([self.atmostProbability(i) for i in range(0, n + 1)])
        return pd.DataFrame({'P(Exactly k)': exactProbs, 'P(Atleast k)': atleastProbs, 'P(Atmost k)': atmostProbs}).rename_axis('k', axis="columns")

    def getRandomNumbers(self, n):
        return self.poissonObj.rvs(n)

    def __getStatsObj(self):
        poissonObj = poisson(self.mu)
        return poissonObj

    def plot(self, n = 10):
        x = range(0, n + 1)
        y = [self.exactProbability(i) for i in range(0, n + 1)]
        data = [go.Bar(x=x, y=y)]
        plotly.offline.init_notebook_mode()
        plotly.offline.iplot(data, filename='jupyter/barchart')

    def getMean(self):
        return round(self.poissonObj.mean(), self.precision)

    def getVariance(self):
        return round(self.poissonObj.var(), self.precision)

    def getStandardDev(self):
        return round(self.poissonObj.std(), self.precision)