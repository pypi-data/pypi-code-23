from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd

from litkit.src.df import info


class OneHotEncoder(BaseEstimator, TransformerMixin):
    def __init__(self, columns=None, dummy_na=None):
        self.columns = columns
        self.dummy_na = dummy_na

    def fit(self, X, y):
        return self

    def transform(self, X: pd.DataFrame):
        for c in self.columns:
            X = X.join(pd.get_dummies(X[c], prefix=c, dummy_na=self.dummy_na))
            del X[c]

        return X


class Info(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame):
        info(X)

        return X
