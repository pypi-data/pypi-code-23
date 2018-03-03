"""Python wrapper for Instagram API.

Instagram rate limit:
sandbox: 500 / hour = 1 / 7.2s
live: 5000 / hour

If in sandbox mode, make sure wait for 8s to make the next request.
"""

import requests

import owl.data.common as common


class MediaInfo(object):
  """Data structure holds common media information.

  Attributes:
    likes: number of likes.
    tags: a list of tag names.
    media_type: image, video.
    filter_type: normal.
    img_*: {"url", "width", "height"},
    loc: {"latitude", "longitude", "name"}
  """
  likes = 0
  tags = None
  media_type = None
  filter_type = None
  created_time = None
  caption_text = None
  media_id = None
  img_low_res = None
  img_thumbnail = None
  img_standard = None
  comments = None
  loc = None

  def parse_json(self, raw_json):
    """Parse raw json data to extract attributes.

    Args:
      raw_json: original json returned by the api.
    """
    try:
      self.likes = raw_json["likes"]["count"]
      self.tags = raw_json["tags"]
      self.media_type = raw_json["type"]
      self.filter_type = raw_json["filter"]
      self.created_time = raw_json["created_time"]
      self.caption_text = raw_json["caption"]["text"]
      self.media_id = raw_json["id"]
      self.img_low_res = {
          "url": raw_json["images"]["low_resolution"]["url"],
          "width": raw_json["images"]["low_resolution"]["width"],
          "height": raw_json["images"]["low_resolution"]["height"]
      }
      self.img_thumbnail = {
          "url": raw_json["images"]["thumbnail"]["url"],
          "width": raw_json["images"]["thumbnail"]["width"],
          "height": raw_json["images"]["thumbnail"]["height"]
      }
      self.img_standard = {
          "url": raw_json["images"]["standard_resolution"]["url"],
          "width": raw_json["images"]["standard_resolution"]["width"],
          "height": raw_json["images"]["standard_resolution"]["height"]
      }
      if raw_json["location"] is not None:
        self.loc = {
            "lat": raw_json["location"]["latitude"],
            "long": raw_json["location"]["longitude"],
            "name": raw_json["location"]["name"]
        }
    except Exception as ex:
      print "error parsing media json: {}".format(ex.message)
      print "raw json: {}".format(raw_json)
      raise Exception


class UserInfo(object):
  """Data structure holds user data.
  """
  pass


class Users(object):
  """User endpoints.

  ref url: https://www.instagram.com/developer/endpoints/users/.
  """
  token = None

  def __init__(self, access_token):
    self.token = access_token

  def get_self_info(self):
    """Get information about the owner of the access_token.

    Returns:
      user data in json.
    """
    response = requests.get(
        "https://api.instagram.com/v1/users/self/?access_token={}".format(
            self.token))
    if response.status_code == 200:
      return response.json()["data"]
    else:
      return None

  def get_user_info(self, user_id):
    """Get information about a user.

    Args:
      user_id: user id.
    Returns:
      user data in json.
    """
    response = requests.get(
        "https://api.instagram.com/v1/users/{}/?access_token={}".format(
            user_id, self.token))
    if response.status_code == 200:
      return response.json()["data"]
    else:
      return None

  def get_self_recent_media(self, min_id=None, max_id=None, count=None):
    """Get the most recent media published by the owner of the access_token.

    Args:
      min_id: return media later than this min_id.
      max_id: return media earlier than this max_id.
      count: count of media to return.
    Returns:
      return media information in json.
    """
    url = "https://api.instagram.com/v1/users/self/media/recent/?"
    url = common.append_url_params(url, {
        "min_id": min_id,
        "max_id": max_id,
        "count": count,
        "access_token": self.token
    })
    response = requests.get(url)
    if response.status_code == 200:
      media_infos = []
      for media_json in response.json()["data"]:
        media_info = MediaInfo()
        media_info.parse_json(media_json)
        media_infos.append(media_info)
      return media_infos
    else:
      return None

  def get_user_recent_media(self,
                            user_id,
                            min_id=None,
                            max_id=None,
                            count=None):
    """Get the most recent media published by a user.

    Args:
      user_id: target user.
      min_id: return media later than this min_id.
      max_id: return media earlier than this max_id.
      count: count of media to return.
    Returns:
      return media information in json.
    """
    url = "https://api.instagram.com/v1/users/{}/media/recent/?".format(
        user_id)
    url = common.append_url_params(url, {
        "min_id": min_id,
        "max_id": max_id,
        "count": count,
        "access_token": self.token
    })
    response = requests.get(url)
    if response.status_code == 200:
      media_infos = []
      for media_json in response.json()["data"]:
        media_info = MediaInfo()
        media_info.parse_json(media_json)
        media_infos.append(media_info)
      return media_infos
    else:
      return None

  def get_self_liked_media(self, count=None, max_like_id=None):
    """Get the list of recent media liked by the owner of the access_token.

    Args:
      count: count of media to return.
      max_like_id: return media liked before this id.
    Returns:
      return media information in json.
    """
    url = "https://api.instagram.com/v1/users/self/media/liked?"
    url = common.append_url_params(url, {
        "count": count,
        "max_lik_id": max_like_id,
        "access_token": self.token
    })
    response = requests.get(url)
    if response.status_code == 200:
      media_infos = []
      for media_json in response.json()["data"]:
        media_info = MediaInfo()
        media_info.parse_json(media_json)
        media_infos.append(media_info)
      return media_infos
    else:
      return None

  def search_users(self, query, count=None):
    """Get a list of users matching the query.

    Args:
      query: user query.
      count: number of users to return.
    Returns:
      a list of users in json.
    """
    url = "https://api.instagram.com/v1/users/search?"
    url = common.append_url_params(
        url, {"q": query,
              "count": count,
              "access_token": self.token})
    response = requests.get(url)
    if response.status_code == 200:
      return response.json()["data"]
    else:
      return None
