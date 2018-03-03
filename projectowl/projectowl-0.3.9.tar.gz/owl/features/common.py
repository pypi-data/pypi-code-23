"""Common data definition.
"""

import abc

import numpy as np


class FeatType(object):
  """Feature type in python.
  """
  # CNN feature.
  CNN_VGGS = 0
  CNN_VGGS_SHORT = 1
  CNN_VGG16 = 2
  CNN_VGG16_SHORT = 3
  CNN_ALEX = 4
  CNN = 6
  # color feature.
  COLOR_CLUSTER = 5
  COLOR_HIST_LINEAR = 6
  COLOR_HIST_JOINT = 7
  # extra.
  CUSTOM = 100


class DistType(object):
  """Distance type.
  """
  L2 = 0
  ANGULAR = 1
  CUSTOM = 2


class ColorSpace(object):
  """Color space name.
  """
  RGB = 0
  BGR = 1
  HSV = 2
  LAB = 3


class FeatParamsBase(object):
  """Base class for feature params.
  """
  feat_type = 0
  feat_name = ""


# map python feature type to c++ feature name.
FeatTypeToNameMapper = {
    FeatType.CNN_VGGS: "cnn_vggs",
    FeatType.CNN_VGGS_SHORT: "cnn_vggs_short",
    FeatType.CNN_VGG16: "cnn_vgg16",
    FeatType.CNN_VGG16_SHORT: "cnn_vgg16_short",
    FeatType.CNN_ALEX: "cnn_alex"
}


def map_name_to_feat_type(feat_name):
  """Map a feature name string to feature type.

  Args:
    feat_name: feature name string.
  """
  for py_type, name in FeatTypeToNameMapper.iteritems():
    if feat_name == name:
      return py_type
  raise ValueError("feat name not exist")


def is_cnn_feat(feat_name):
  """Check if a feature name is cnn feature.

  Args:
    feat_name: feature name string.
  """
  if feat_name in FeatTypeToNameMapper.values():
    return True
  else:
    return False


class BaseFeatParams(object):
  """Base class for feature extractor params.

  Put feature related params here.
  """
  pass


class BaseFeatExtractor(object):
  """Base class for feature extraction.

  Generic usage of a feature extractor:
  1) create: my_extractor = MyFeature(feat_params)
  2) start (load trainable feature, e.g. dnn, bow): my_extractor.start()
  3) set input: my_extractor.set_input(color_img) or
  4) compute feature: my_extractor.compute(color_img, mask)
  5) compare feature: my_extractor.calc_dist(feat1, feat2)

  Attributes:
    feat_tpye: type of feature.
    feat_name: name of feature.
    feat_params: feature parameters.
    raw_img_bgr: original bgr image.
    internal_img: intermediate image representation, e.g. gray image.
  """
  __metaclass__ = abc.ABCMeta

  feat_type = None
  feat_name = None
  feat_dim = 0
  feat_params_ = None
  raw_img_rgb = None
  internal_img = None

  @abc.abstractmethod
  def __init__(self, feat_params=None):
    """Initialize feature extractor.

    Override to set property of the extractor.

    Args:
      feat_params: parameters for feature extractor.
    """
    pass

  def set_input(self, rgb_img):
    """Set input image and preprocess it.

    This is useful for repeated feature extraction from
    the same image with shared middle data.

    Args:
      rgb_img: 3D numpy array as rgb image.
    """
    self.raw_img_rgb = rgb_img

  def start(self):
    """Prepare feature extractor.
    """
    print "feature {} started".format(self.feat_name)

  @abc.abstractmethod
  def compute(self, rgb_img=None, mask=None):
    """Compute image feature.

    Args:
      rgb_img: input image. If none, use internal image.
      mask: pixel mask. non-zero indicates valid.
    Returns:
      1D ndarray feature vector.
    """
    pass

  def compute_batch(self, rgb_imgs, masks=None):
    """Compute image features in batch.

    Args:
      rgb_imgs: a list of rgb_img.
    Returns:
      batch features as 2D matrix, each row is a feature vector.
    """
    feats = []
    for idx, rgb_img in enumerate(rgb_imgs):
      if masks is not None:
        cur_feat = self.compute(rgb_img, masks[idx])
      else:
        cur_feat = self.compute(rgb_img)
      feats.append(cur_feat)
    return np.stack(feats)

  @abc.abstractmethod
  def calc_dist(self, feat1, feat2):
    """Compute distance between two feature vectors.

    Used for custom distance metric.

    Args:
      feat1: first feature vector.
      feat2: second feature vector.
    Returns:
      float distance value.
    """
    pass

  def get_feat_dim(self):
    """Return feature dimenion.
    """
    return self.feat_dim
