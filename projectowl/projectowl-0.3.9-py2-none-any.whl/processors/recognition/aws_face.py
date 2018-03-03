"""Face processors based on aws rekognition.
"""

import json

from owl.data.img_obj import OwlImage
from owl.processors.recognition import common
from owl.third.vision.rekognition_api import AWSRekognitionAPI
from owl.pipelines.recognition.img_det.pipeline import ImgDetectionPipeline


class AWSFaceDetector(common.ImgDetectorBase):
  """Face detector using aws.
  """
  engine = None

  def __init__(self, access_key, secret_key, region):
    self.engine = AWSRekognitionAPI(access_key, secret_key, region)

  def prepare(self):
    pass

  def predict(self, img):
    raw_res = self.engine.detect_faces(img.to_binary())
    new_res = common.ImgDetPred()
    new_res.img_ref = img.to_datauri()
    for face in raw_res:
      face_box = (int(face["BoundingBox"]["Left"] * img.width()),
                  int(face["BoundingBox"]["Top"] * img.height()),
                  int(face["BoundingBox"]["Width"] * img.width()),
                  int(face["BoundingBox"]["Height"] * img.height()))
      new_res.bboxes.append(face_box)
      new_res.box_labels.append(face["Gender"]["Value"])
      new_res.box_scores.append(face["Confidence"])
    return new_res


if __name__ == "__main__":
  with open("../../third/aws_config.json", "r") as f:
    config = json.load(f)
  face_detector = AWSFaceDetector(config["access_key"], config["secret_key"],
                                  config["region"])
  img = OwlImage(fp="../../assets/group_faces.jpg")
  det_pipeline = ImgDetectionPipeline(face_detector)
  det_preds = det_pipeline.predict([img])
  det_pipeline.show(det_preds,
                    "/mnt/Lab/results/owlpipelines/aws_facedet.html")
