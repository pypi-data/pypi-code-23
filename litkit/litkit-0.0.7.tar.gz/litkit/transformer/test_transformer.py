import unittest

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from litkit.data import get_baseball_df
from litkit.inspect import info
from litkit.transformer import OneHotEncoder, ScopedTransformer


class TestTransformer(unittest.TestCase):
    def test_OneHotEncoder(self):
        df = get_baseball_df()

        p = Pipeline([
            ('e', OneHotEncoder(columns=['League']))
        ])

        df = p.transform(df)

        info(df)

    def test_ScopedTransformer(self):
        df = get_baseball_df()

        p = Pipeline([
            ('e', ScopedTransformer(transformer=MinMaxScaler(), columns=['RS']))
        ])

        df = p.fit_transform(df, [])

        info(df)
