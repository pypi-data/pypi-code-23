"""Test tumblr api.
"""

import unittest

from owl.third.social import tumblr


class TumblrAPITester(unittest.TestCase):
  def test_client(self):
    api = tumblr.TumblrAPI()
    items = api.crawl_posts("street style", to_continue=True)
    items2 = api.crawl_posts("street style", to_continue=True)
    items.extend(items2)
    for item in items:
      print item["img_urls"]
      print ""


if __name__ == "__main__":
  unittest.main()
