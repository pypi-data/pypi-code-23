"""Tests for vision api.
"""

import unittest

import owl.data.img_tools as img_tools
import owl.third.aws as owl_aws
import owl.third.vision as vision_api


class VisionAPITester(unittest.TestCase):
  test_img_fn = "/mnt/Lab/imgs/1_25_25389.jpg"
  test_img_url = "https://static1.squarespace.com/static/58b4437f03596e617b3ebd07/58b5c7b8d2b857059b9b705b/58b5c7bdd1758ecc1d4a86ff/1488308168310/eg3.png"

  def test_clarifai(self):
    api_key = "c87f6abeb46f41f1baabb014626a4d23"
    api = vision_api.clarifai_api.ClarifaiAPI(api_key)
    res = api.label_img_general(img_fn=self.test_img_fn)
    print res
    # res = api.label_img_general(self.test_img_url)

  def test_rekognition(self):
    credentials = owl_aws.common.read_config_fn("../aws_config.json")
    api = vision_api.rekognition_api.RekognitionAPI(credentials["access_key"],
                                                    credentials["secret_key"],
                                                    credentials["region"])
    img_bin = img_tools.read_img_bin(self.test_img_fn)
    res = api.label_img(img_bin)
    print res

  def test_google(self):
    pass


if __name__ == "__main__":
  unittest.main()
