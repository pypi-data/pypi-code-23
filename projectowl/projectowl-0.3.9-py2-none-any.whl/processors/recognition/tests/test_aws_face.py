import json

from owl.processors.recognition import aws_face


class AWSFaceTester(object):
  aws_configs = None

  def __init__(self):
    with open("./aws_config.json", "r") as f:
      self.aws_configs = json.load(f)

  def test_face_detect(self):
    face_det = aws_face.AWSFaceDetector(self.aws_configs["access_key"],
                                        self.aws_configs["secret_key"],
                                        self.aws_configs["region"])
    test_img_path = ""