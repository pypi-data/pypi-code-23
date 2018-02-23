"""Tests for dynamodb.
"""

import unittest
import time

from owl.third import aws

access_key = "AKIAILIZOLWO7H6IZVPA"
secret_key = "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"


class DynamodbTester(unittest.TestCase):
  def test_load_time(self):
    """Test how long does it take to load database from cloud.
    """
    try:
      dynamodb = aws.DynamoDBIO(
          access_key=access_key, secret_key=secret_key, region="us-east-1")
      dynamodb.use_table("products_metadata")
      # test loading 1000 item time.
      all_items = []
      startt = time.time()
      cont_key = None
      req_num = 0
      while len(all_items) < 5000:
        items, cont_key = dynamodb.scan_items(cont_key=cont_key)
        all_items.extend(items)
        req_num += 1
        print "request number: {}".format(req_num)
        if cont_key is None:
          break
      print "item count: {}".format(len(all_items))
      print "one scan time cost: {}s".format(time.time() - startt)
    except Exception as ex:
      print ex.message


if __name__ == "__main__":
  unittest.main()
