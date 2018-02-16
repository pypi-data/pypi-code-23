import unittest

from sklearn.pipeline import Pipeline

from litkit.src.data import get_baseball_df
import litkit as lk
from litkit.src.transformer.transformer import OneHotEncoder


class TestTransformer(unittest.TestCase):
    def test_OneHotEncoder(self):
        df = get_baseball_df()

        p = Pipeline([
            ('e', OneHotEncoder(columns=['League']))
        ])

        df = p.transform(df)

        lk.df.info(df)
