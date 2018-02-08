import unittest

from plotlog.datacut import DataCut


class TestDataCut(unittest.TestCase):
    def setUp(self):
        self.data = DataCut("../test/log/170101000000.csv")
        self.assertTrue("../test/log/170101000000.csv")

    def tearDown(self):
        self.data.dispose()

    def test_import_logfile(self):
        self.data.import_file(0, ",")
        self.assertIsNotNone(self.data.df)

    def test_import_logfile_no_use_header(self):
        self.data.import_file(None, ",")
        self.assertEqual(self.data.df.columns[2], 2)

    def test_df_x_axis(self):
        self.data.import_file(0, ",")
        self.data.set_x_axis("x")
        self.assertEqual(self.data.x_axis[0], 0.0)
        self.data.set_x_axis(0)
        self.assertEqual(self.data.x_axis[0], 0.0)

    def test_df_shift(self):
        self.data.import_file(0, ",")
        self.data.set_x_axis("x")
        self.data.shift("trig", [-1e-5, 1e-5])
        self.assertEqual(self.data.x_axis[0], 0.0)
        self.assertTrue(self.data.df["trig"][0] < 0.001)
        self.assertTrue(self.data.df["trig"][1] > 0.001)

    def test_df_shift_head(self):
        self.data.import_file(0, ",")
        self.data.set_x_axis("x")
        self.data.shift("cos", [-1e-5, 1e-5])
        self.assertEqual(self.data.x_axis[0], 0.0)
        self.assertEqual(self.data.df["sin"][0], 0.0)
        self.assertEqual(self.data.df["cos"][0], 1/3)

    def test_df_slice(self):
        self.data.import_file(0, ",")
        self.data.set_x_axis("x")
        self.data.slice((5.0, 10.0))
        self.assertEqual(self.data.x_axis[0], 5.0)
        self.assertEqual(self.data.x_axis.tail(1).values[0], 10.0)
        self.assertEqual(len(self.data.x_axis), len(self.data.df))


if __name__ == '__main__':
    unittest.main()
