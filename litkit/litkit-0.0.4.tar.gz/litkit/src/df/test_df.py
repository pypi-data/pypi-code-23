import unittest

from litkit.src.data import get_baseball_df
from litkit.src.df import info


class TestDf(unittest.TestCase):
    def test_info(self):
        df = get_baseball_df()

        info(df)
