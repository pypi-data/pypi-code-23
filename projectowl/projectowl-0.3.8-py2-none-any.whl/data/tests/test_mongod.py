"""Test mongodb manager.
"""

import time

import unittest
from owl.data import mongo_manager

class MongoDBTester(unittest.TestCase):
  db = mongo_manager.MongoManager()

  def test_query_speed(self):
    self.db.connect(db_name="eyestyle_production", collection_name="products_2016_02")
    startt = time.time()
    items = self.db.query(attribute="category", value_list=["casual-pants"], limit=0)
    print "query category time: {}s, items: {}".format(time.time()-startt, len(items))

if __name__ == "__main__":
  unittest.main()
