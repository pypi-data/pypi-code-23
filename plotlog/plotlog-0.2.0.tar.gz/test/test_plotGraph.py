import unittest

from plotlog.datacut import DataCut
from plotlog.plotgraph import PlotGraph
from plotlog.setting import Setting

from os import makedirs


class TestPlotGraph(unittest.TestCase):
    def setUp(self):
        self.st = Setting("user.yml")
        self.st.configure()
        self.data = DataCut("../test/log/170101000000.csv")
        self.data.import_file(0, ",")
        self.data.set_x_axis("x")
        self.pg = PlotGraph()

    def tearDown(self):
        self.data.dispose()

    def test_plot_graph(self):
        makedirs("graph/other/test", exist_ok=True)
        for stg in self.st.graph:
            path = "graph/other/test/test_"+stg["name"]+".png"
            self.pg.plot("graph/other/test", path, self.st.setting, stg,
                         self.data.x_axis, self.data.df)


if __name__ == '__main__':
    unittest.main()
