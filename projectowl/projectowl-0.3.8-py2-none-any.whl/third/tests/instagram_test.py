"""Instagram api test.
"""

import unittest

from owl.third import instagram

access_token = "290412779.f188e2f.d6e2d8c4cde74eab8a96564a3b1fbb14"


class InstagramUserTest(unittest.TestCase):
  """Class to test user endpoints.
  """
  user_api = instagram.Users(access_token)

  def test_get_self(self):
    self_info = self.user_api.get_self_info()
    self.assertIsNotNone(self_info)

  def test_get_self_media(self):
    count = 30
    media_infos = self.user_api.get_self_recent_media(count=count)
    self.assertEqual(len(media_infos), count)


if __name__ == "__main__":
  unittest.main()
