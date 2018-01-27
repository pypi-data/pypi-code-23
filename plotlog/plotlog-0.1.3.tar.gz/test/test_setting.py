import unittest
from src.setting import Setting


class TestSetting(unittest.TestCase):
    def setUp(self):
        self.obj = Setting("test/test.yml")
        self.obj.configure()

    def tearDown(self):
        self.obj.dispose()

    def test_config_setting_dic(self):
        self.assertEqual(len(self.obj.graph), 2)
        self.assertNotEqual(self.obj.setting["put_log_dir"],
                            self.obj.default["put_log_dir"])
        # self.assertNotEqual(self.obj.setting["footprint"]["foot_size"],
        #                     self.obj.default["footprint"]["foot_size"])
        # self.assertEqual(self.obj.setting["footprint"]["supleg_label"],
        #                  self.obj.default["footprint"]["supleg_label"])

    def test_config_graph_dic(self):
        self.assertEqual(len(self.obj.graph), 2)
        self.assertNotEqual(self.obj.graph[0]["xlabel"],
                            self.obj.default["graph"][0]["xlabel"])
        self.assertEqual(self.obj.graph[0]["xlabel"], "time[s]")
        self.assertEqual(self.obj.graph[0]["ylim"],
                         self.obj.default["graph"][0]["ylim"])
        self.assertEqual(len(self.obj.graph[0]["plot"]), 6)
        self.assertTrue("color" in self.obj.graph[0]["plot"][0])
        self.assertEqual(self.obj.graph[0]["legend"]["loc"], "best")
        self.assertIsNotNone(self.obj.graph[1]["legend"]["ncol"])


if __name__ == '__main__':
    unittest.main()
