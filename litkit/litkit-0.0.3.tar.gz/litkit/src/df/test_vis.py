import unittest

from litkit.src.data import get_baseball_df
from litkit.src.df.vis import scatter_matrix


class TestVis(unittest.TestCase):
    def test_scatter_matrix(self):
        df = get_baseball_df()

        scatter_matrix(df)
