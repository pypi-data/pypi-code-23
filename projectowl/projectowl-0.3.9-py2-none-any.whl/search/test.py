"""Test search components.
"""

import unittest

from owl.search import multi_index_fusion


class MultiIndexFusionTester(unittest.TestCase):
  def test_fusion(self):
    dummy_res = [None] * 3
    dummy_res[0] = {
        "data": [("1", 0.32), ("3", 0.22), ("4", 0.98)],
        "weight": 0.5
    }
    dummy_res[1] = {"data": [("1", 0.45), ("4", 0.34)], "weight": 0.2}
    dummy_res[2] = {"data": [("1", 0.3), ("3", 0.65)], "weight": 0.8}
    fuser = multi_index_fusion.MultiIndexFusion()
    final_res = fuser.group_and_rerank(dummy_res)
    print final_res


if __name__ == "__main__":
  unittest.main()
