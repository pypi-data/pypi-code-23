import unittest

from src.datacut import DataCut
from src.plotgraph import PlotGraph
from src.setting import Setting


class TestPlotGraph(unittest.TestCase):
    def setUp(self):
        self.st = Setting("test.yml")
        self.st.configure()
        self.data = DataCut("../test/log/201712251354.csv")
        self.data.import_file(0, ",")
        self.data.set_x_axis("time")
        self.pg = PlotGraph()

    def tearDown(self):
        self.data.dispose()

    def test_plot_graph(self):
        for stg in self.st.graph:
            path = "graph/other/test/test_"+stg["name"]+".png"
            self.pg.plot("graph/other/test", path, self.st.setting, stg,
                         self.data.x_axis, self.data.df)


if __name__ == '__main__':
    unittest.main()
