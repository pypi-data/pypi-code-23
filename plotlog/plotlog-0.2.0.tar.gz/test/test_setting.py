import unittest
from plotlog.setting import Setting


class TestSetting(unittest.TestCase):
    def setUp(self):
        self.obj = Setting("user.yml")
        self.obj.configure()

    def tearDown(self):
        self.obj.dispose()

    def test_config_setting_dic(self):
        self.assertEqual(len(self.obj.graph), 2)
        self.assertEqual(self.obj.setting["put_log_dir"],
                         self.obj.default["put_log_dir"])

    def test_config_graph_dic(self):
        self.assertNotEqual(self.obj.graph[0]["xlabel"], "")
        self.assertEqual(self.obj.graph[0]["xlabel"], "x")
        self.assertEqual(self.obj.graph[0]["ylim"], [-1.5, 1.5])
        self.assertEqual(len(self.obj.graph[0]["plot"]), 4)
        self.assertTrue("color" in self.obj.graph[0]["plot"][0])
        self.assertEqual(self.obj.graph[0]["legend"]["loc"], "best")
        self.assertIsNotNone(self.obj.graph[1]["do_subplot"][1]["legend"]["ncol"])


if __name__ == '__main__':
    unittest.main()
