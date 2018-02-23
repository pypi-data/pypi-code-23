"""Basic recognition processor objects.

All the object structures are agnostic to actual algorithm.
These are prediction interfaces.
"""

import abc
import random

from owl.data.img_obj import OwlImage
""" Image classification """


class ImgClfPred(object):
  """Class for image classification result.
  """
  img_ref = None
  scored_labels = None

  def __init__(self, label_scores=None):
    """Create object from a list of scored labels.

    Args:
      scored_labels: [(label_name, label_score)].
      Compatible with deepmodels classifier output.
    """
    if label_scores:
      self.scored_labels = []
      for label_score in label_scores:
        self.scored_labels.append(
            (label_score[0], format(label_score[1], ".4f")))

  def to_json(self):
    return {"img_ref": self.img_ref, "labels": self.scored_labels}


class ImgClassifierBase(object):
  """Base class for image classification processors.
  """
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def __init__(self):
    pass

  @abc.abstractmethod
  def prepare(self):
    """Prepare prediction model.
    """
    pass

  @abc.abstractmethod
  def predict(self, img):
    """Take input of OwlImg and output ImgClfPred.

    Returns: ImgClfRes object.
    """
    assert isinstance(img, OwlImage)


""" Image detection """


class ImgDetPred(object):
  """Class for image detection result.
  """
  img_ref = None
  # list of bounding box: <xmin, ymin, width, height>.
  bboxes = []
  box_labels = []
  box_scores = []


class ImgDetectorBase(object):
  """Base class for image detection processors.
  """
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def __init__(self):
    pass

  @abc.abstractmethod
  def prepare(self):
    """Prepare prediction model.
    """
    pass

  @abc.abstractmethod
  def predict(self, img):
    pass

  def vis_preds(self, img, pred):
    """Draw detection boxes on image.
    """
    line_colors = []
    texts = []
    for idx in range(len(pred.bboxes)):
      cur_color = (random.randint(0, 255), random.randint(0, 255),
                   random.randint(0, 255))
      line_colors.append(cur_color)
      texts.append(str(idx))
    new_img = img.draw_boxes(
        pred.bboxes, line_colors=line_colors, line_width=3, texts=texts)
    return new_img
