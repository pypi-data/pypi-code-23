from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
from sklearn.preprocessing import Imputer as sk_Imputer

from litkit.src.df import info


# todo: inject full distribution, otherwise the cv folds won"t contain all possible categories
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


class Imputer(BaseEstimator, TransformerMixin):
    def __init__(self, strategy=None):
        self.strategy = strategy
        self.imputer = None

    def fit(self, X, y=None):
        if self.strategy == '0':
            return self

        self.imputer = sk_Imputer(strategy=self.strategy)
        self.imputer.fit(X, y)

        return self

    def transform(self, X):
        if self.strategy == '0':
            return X.fillna(value=0)

        d = self.imputer.transform(X)

        return pd.DataFrame(d, index=X.index, columns=X.columns)


class Keeper(BaseEstimator, TransformerMixin):
    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.columns]


class Info(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame):
        info(X)

        return X


class ScopedTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, transformer=None, columns=None):
        self.transformer = transformer
        self.columns = columns

    def fit(self, X, y=None):
        self.transformer.fit(X[self.columns], y)

        return self

    def transform(self, X):
        X[self.columns] = self.transformer.transform(X[self.columns])

        return X
