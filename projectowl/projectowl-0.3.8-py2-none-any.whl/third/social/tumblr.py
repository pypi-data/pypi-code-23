"""Tumblr api.

Wrapper above offical api.
Install: pip install git+https://github.com/tumblr/pytumblr
"""

import sys

import pytumblr

from owl.data import common


class TumblrAPI(object):
  """High-level task manager using official tumblr api.

  NOTE: tumblr limites 1000 requests per hour and 5000 per day.
  """
  # keys: associated with eyestyle app.
  consumer_key = "rXnjXHodcwWevFSyn4SPna57z11Si68lhDXLEPALaIVxBtVrwe"
  consumer_secret = "lpANgcmY0KtWJjESMNTbeJpHCJawDz1LpHkLcLTLSnmcQJjO3k"
  token = "lLImTDSPUkwPUK63fySRv0NYHJBmF7NlMnAMV9g7IB8NxbQH4y"
  token_secret = "9xT1CMdO6rrxt11rI6ydQVRi8G15WB0MNgWBaVnGrjfblJQTJH"
  api_key = "rXnjXHodcwWevFSyn4SPna57z11Si68lhDXLEPALaIVxBtVrwe"
  # client object.
  client = None
  # key used to continue crawl.
  cont_key = None

  def __init__(self):
    # init client.
    self.client = pytumblr.TumblrRestClient(
        self.consumer_key, self.consumer_secret, self.token, self.token_secret)

  def set_initial_cont_key(self, key):
    """Set the initial continue key to start.
    """
    self.cont_key = key

  def crawl_posts(self, tag, only_photo=True, to_continue=False):
    """Crawl posts given a specific tag.

    Args:
      tag: keyword used to crawl images.
      num: number of posts to return.
      only_photo: only return photo post.
      cont_key: key used to continue fetch.
    Returns:
      items meet options.
    """
    try:
      # make request.
      if to_continue and self.cont_key is not None:
        res = self.client.tagged(tag, before=self.cont_key)
      else:
        res = self.client.tagged(tag)
      # exceeds limit
      if "meta" in res:
        raise ValueError("exceeds tumblr limit")
      # parse objects.
      items = []
      oldest_timestamp = sys.maxint
      for item in res:
        if only_photo and item["type"] != "photo":
          continue
        if "featured_timestamp" in item:
          oldest_timestamp = min(item["featured_timestamp"], oldest_timestamp)
        else:
          oldest_timestamp = min(item["timestamp"], oldest_timestamp)
        # parse image urls.
        if "photos" in item:
          img_urls = []
          for photo in item["photos"]:
            img_urls.append(photo["original_size"]["url"])
          item["img_urls"] = img_urls
        items.append(item)
      if to_continue:
        self.cont_key = oldest_timestamp
      return items
    except Exception as ex:
      raise Exception(
          common.get_detailed_error_msg(ex.message, sys.exc_info()))
