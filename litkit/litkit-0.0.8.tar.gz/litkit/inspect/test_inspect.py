import unittest

from litkit.data import get_baseball_df
from litkit.inspect import info


class TestDf(unittest.TestCase):
    def test_info(self):
        df = get_baseball_df()

        info(df)

        info(df.values)
