import os
import random

from owl.processors.recognition.common import ImgClfPred, ImgClassifierBase
from owl.pipelines.recognition.img_clf.pipeline import ImgClassificationPipeline


class DummyImgClf(ImgClassifierBase):
  def __init__(self):
    pass

  def prepare(self):
    pass

  def predict(self, imgs):
    pass


class TestImgClfPipeline(object):
  img_dir = "/mnt/Lab/imgs/salientobj/data/"

  def test_display(self):
    dummy_preds = []
    imgs = os.listdir(self.img_dir)
    imgs = [os.path.join(self.img_dir, x) for x in imgs]
    for i in range(30):
      cur_pred = ImgClfPred()
      cur_pred.img_ref = imgs[i]
      cur_pred.label_names = ["dog", "cat", "cow", "apple", "pear", "peach"]
      cur_pred.label_scores = [random.random()] * 6
      dummy_preds.append(cur_pred)
    pp = ImgClassificationPipeline(DummyImgClf())
    pp.show(dummy_preds, "/mnt/Lab/results/owlpipelines/imgclf.html")
