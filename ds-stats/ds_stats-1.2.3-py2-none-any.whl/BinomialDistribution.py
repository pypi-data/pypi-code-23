from scipy.stats import binom
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go

class BinomialDistribution:
    def __init__(self, n, p, precision = 4):
        self.n = n
        self.p = p
        self.precision = precision
        self.binomObj = binom(self.n, self.p)

    def exactProbability(self, k):
        prob = self.binomObj.pmf(k)
        return round(prob, self.precision)

    def atleastProbability(self, k):
        lst = [self.binomObj.pmf(i) for i in range(k, self.n+1)]
        prob = sum(lst)
        return round(prob, self.precision)

    def atmostProbability(self, k):
        lst = [self.binomObj.pmf(i) for i in range(0, k+1)]
        prob = sum(lst)
        return round(prob, self.precision)

    def generateTable(self):
        exactProbs = np.array([self.exactProbability(i) for i in range(0, self.n + 1)])
        atleastProbs = np.array([self.atleastProbability(i) for i in range(0, self.n + 1)])
        atmostProbs = np.array([self.atmostProbability(i) for i in range(0, self.n + 1)])
        return pd.DataFrame({'P(Exactly k)': exactProbs, 'P(Atleast k)': atleastProbs, 'P(Atmost k)': atmostProbs}).rename_axis('k', axis="columns")

    def getRandomNumbers(self, n):
        return self.binomObj.rvs(n)

    def plot(self):
        x = range(0, self.n + 1)
        y = [self.exactProbability(i) for i in range(0, self.n + 1)]
        data = [go.Bar(x=x, y=y)]
        plotly.offline.init_notebook_mode()
        plotly.offline.iplot(data, filename='jupyter/barchart')

    def getMean(self):
        return round(self.binomObj.mean(), self.precision)

    def getVariance(self):
        return round(self.binomObj.var(), self.precision)

    def getStandardDev(self):
        return round(self.binomObj.std(), self.precision)