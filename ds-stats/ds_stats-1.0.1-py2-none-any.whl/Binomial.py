from scipy.stats import binom
import pandas as pd
import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

class Binomial:
    def __init__(self, n, p):
        self.n = n
        self.p = p

    def exactProbability(self, k, precision = 4):
        prob = binom.pmf(k, self.n, self.p)
        return round(prob, precision)

    def atleastProbability(self, k, precision = 4):
        lst = [binom.pmf(i, self.n, self.p) for i in range(k, self.n+1)]
        prob = sum(lst)
        return round(prob, precision)

    def atmostProbability(self, k, precision = 4):
        lst = [binom.pmf(i, self.n, self.p) for i in range(0, k+1)]
        prob = sum(lst)
        return round(prob, precision)

    def generateTable(self, precision = 4):
        exactProbs = np.array([self.exactProbability(i, precision) for i in range(0, self.n + 1)])
        atleastProbs = np.array([self.atleastProbability(i, precision) for i in range(0, self.n + 1)])
        atmostProbs = np.array([self.atmostProbability(i, precision) for i in range(0, self.n + 1)])
        return pd.DataFrame({'P(Exactly k)': exactProbs, 'P(Atleast k)': atleastProbs, 'P(Atmost k)': atmostProbs}).rename_axis('k', axis="columns")

    def plot(self, precision = 4):
        x = range(0, self.n + 1)
        y = [self.exactProbability(i, precision) for i in range(0, self.n + 1)]
        data = [go.Bar(x=x, y=y)]
        plotly.offline.init_notebook_mode()
        plotly.offline.iplot(data, filename='jupyter/barchart')

    def getMean(self, precision = 4):
        return round(binom.mean(self.n, self.p), precision)

    def getVariance(self, precision = 4):
        return round(binom.var(self.n, self.p), precision)

    def getStandardDev(self, precision = 4):
        return round(binom.std(self.n, self.p), precision)