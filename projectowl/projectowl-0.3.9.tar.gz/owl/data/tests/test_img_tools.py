"""Tests for image tools module.
"""

import unittest

from owl.data import img_tools


class ImgToolsTester(unittest.TestCase):
  def test_img_bin_to_numpy(self):
    img_fn = "/mnt/Lab/imgs/1_25_25389.jpg"
    img_bin = img_tools.read_img_bin(img_fn)
    img_arr = img_tools.img_bin_to_numpy_rgb(img_bin)
    print img_arr.shape
    self.assertLess(img_arr.shape[0], img_arr.shape[1])


if __name__ == "__main__":
  unittest.main()
