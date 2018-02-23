"""Tests for visualsearch pipeline.
"""

import unittest

from owl.pipelines.visualsearch import visualsearch


class VisualSearchTester(unittest.TestCase):
  res_dir = "/mnt/DataHouse/Fashion/EyeStyle/cnn_test/pipeline/test1/res_test/"
  img_dir = "/mnt/DataHouse/Fashion/EyeStyle/cnn_test/pipeline/test1/data/"
  pipe = visualsearch.OneFeatVisualSearcher("vs_test", res_dir)

  def test_file_loading(self):
    self.pipe.read_data_from_files(self.img_dir, ["*.jpg"])

  def test_db_loading(self):
    self.pipe.load_items_from_db()

  def test_dev(self):
    self.pipe.start_dev(None)
    self.pipe.run_dev(
        self.img_dir, ["*.jpg"],
        load_items_from_db=False,
        compute_feats=True,
        compress_feats=True,
        train_compressor=True)

  def test_deploy(self):
    self.pipe.start_deploy(None)
    query_img = None
    res_data = self.pipe.search(query_img, 1000)


if __name__ == "__main__":
  unittest.main()
