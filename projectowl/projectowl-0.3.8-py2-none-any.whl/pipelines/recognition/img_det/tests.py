import os
import random

from owl.data.img_obj import OwlImage
from owl.processors.recognition.common import ImgDetPred, ImgDetectorBase
from owl.pipelines.recognition.img_det.pipeline import ImgDetectionPipeline


class DummyImgDet(ImgDetectorBase):
  def __init__(self):
    pass

  def prepare(self):
    pass

  def predict(self, imgs):
    pass


class TestImgDetPipeline(object):
  img_dir = "/mnt/Lab/imgs/salientobj/data/"

  def test_display(self):
    dummy_preds = []
    imgs = os.listdir(self.img_dir)
    imgs = [os.path.join(self.img_dir, x) for x in imgs]
    for i in range(30):
      cur_pred = ImgDetPred()
      cur_pred.box_labels = ["dog", "cat", "cow", "apple", "pear", "peach"]
      cur_pred.box_scores = [random.random()] * 6
      cur_pred.bboxes = [(10, 10, 120, 110)] * 6
      cur_img = OwlImage(fp=imgs[i])
      cur_img.img_arr = cur_img.draw_box(cur_pred.bboxes[0], line_width=3)
      cur_pred.img_ref = cur_img.to_datauri()
      dummy_preds.append(cur_pred)
    pp = ImgDetectionPipeline(DummyImgDet())
    pp.show(dummy_preds, "/mnt/Lab/results/owlpipelines/imgdet.html")
