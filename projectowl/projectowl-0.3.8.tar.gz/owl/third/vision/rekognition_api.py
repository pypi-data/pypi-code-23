"""AWS ReKognition api manager.

Need aws account and assign rekognition permission.
"""

import json

from owl.data import img_tools
from owl.third.aws import common as aws_common


class AWSRekognitionAPI(aws_common.AWSService):
  """Class for managing aws rekognition api.
    """

  def __init__(self, access_key, secret_key, region):
    """Create rekognition client.
    """
    self.init_aws("rekognition", access_key, secret_key, region)

  def label_img(self, img_bin, top_k=10):
    """Predict image labels.

    Args:
      img_bin: binary image data.
      top_k: top k predictions.
    Returns:
      a list of predicted labels and probability, e.g. [("dog", 0.65)]
    """
    res = self.client.detect_labels(Image={"Bytes": img_bin}, MaxLabels=top_k)
    new_res = []
    for item in res["Labels"]:
      new_res.append((item["Name"], item["Confidence"]))
    return new_res

  def detect_faces(self, img_bin):
    """Detect faces in given image.

    Api ref: http://boto3.readthedocs.io/en/latest/reference/services/rekognition.html#Rekognition.Client.detect_faces

    Args:
      img_bin: image binary data.
    
    Returns:
      a list of face details.
    """
    res = self.client.detect_faces(
        Image={"Bytes": img_bin}, Attributes=["ALL"])
    res_data = res["FaceDetails"]
    return res_data

  def detect_celebrities(self, img_bin):
    """Detect celebrities in a given image.

    Args:
      img_bin: image binary data.

    Returns:
      a list of detected celebrities details.
    """
    res = self.client.recognize_celebrities(Image={"Bytes": img_bin})
    return res["CelebrityFaces"]

  def detect_text(self, img_bin):
    """Detect text in image.

    Args:
      img_bin: binary image data.

    Returns:
      a list of detected text.
    """
    res = self.client.detect_text(Image={"Bytes": img_bin})
    text_res = []
    for det_res in res["TextDetections"]:
      cur_res = {}
      cur_res["text"] = det_res["DetectedText"]
      cur_res["bbox"] = det_res["Geometry"]["BoundingBox"]
      cur_res["score"] = det_res["Confidence"]
      text_res.append(cur_res)
    return text_res


if __name__ == "__main__":
  with open("../aws_config.json", "r") as f:
    config = json.load(f)
  api = AWSRekognitionAPI(config["access_key"], config["secret_key"],
                          config["region"])
  img = img_tools.read_img_bin("../../assets/bird.jpg")
  labels = api.label_img(img)
  texts = api.detect_text(img)
  print labels
  print texts