from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


class OneHotEncoder(BaseEstimator, TransformerMixin):
    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y):
        return self

    def transform(self, X: pd.DataFrame):
        for c in self.columns:
            X = X.join(pd.get_dummies(X[c], prefix=c))
            del X[c]

        return X