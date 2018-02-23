"""Service to detect objects in image.
"""

import os
from tqdm import tqdm
from jinja2 import Environment, FileSystemLoader

from owl.processors.recognition.common import ImgDetPred, ImgDetectorBase


class ImgDetectionPipeline(object):
  """Class for image classification pipeline.
  """
  model = None

  def __init__(self, model_):
    """Set up prediction model.
    """
    assert isinstance(model_, ImgDetectorBase), "incorrect model type."
    self.model = model_

  def prepare(self):
    self.model.prepare()

  def predict(self, input_imgs):
    """Make prediction for images.

    Args:
      input_imgs: a list of owlimage objects.
    """
    print "start predicting images..."
    preds = []
    for cur_img in tqdm(input_imgs):
      cur_pred = self.model.predict(cur_img)
      vis_img = self.model.vis_preds(cur_img, cur_pred)
      vis_img.show("detect")
      cur_pred.img_ref = vis_img.to_datauri()
      preds.append(cur_pred)
    return preds

  def show(self, preds, save_fn):
    """Show predictions in a web page.
    """
    assert save_fn[-4:] == "html", "save file must be an html file."
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(cur_dir), trim_blocks=True)
    res_str = j2_env.get_template("./app/index.html").render(
        name="test", preds=preds)
    with open(save_fn, "w") as fn:
      fn.write(res_str)
      print("results saved to {}".format(save_fn))


if __name__ == "__main__":
  pass