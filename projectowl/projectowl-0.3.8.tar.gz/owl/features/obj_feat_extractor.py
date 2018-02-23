"""Generic interface for feature extraction.
"""

import os
import cv2

import commentjson
from owl.features import common


class GenericObjFeatExtractor(object):
  """Python interface for feature extraction.

  Generic interface for extracting different features for an object.
  """

  # list of feature extractors.
  feat_extractors = {}
  raw_img_rgb = None
  inside_img = None
  config_fn = ""

  def __init__(self, config_fn="", features=None):
    """Create extractor.

    Supports init from config file or passed extractors.
    If both are present, combine them all.

    Args:
      config_fn: json file with feature configuration.
    Used for built-in features.
      features: a list of custom defined features.
    """
    if config_fn != "":
      self.init_with_fn(config_fn)
    if features is not None:
      self.init_from_features(features)

  def init_with_fn(self, config_fn):
    """Create extractor from configure file.

    Args:
      config_fn: json configuration file.
    """
    self.config_fn = config_fn

    # init python part
    with open(config_fn, 'r') as f:
      config = commentjson.load(f)

    # extract features
    feat_configs = config['engine']['features']
    for feat_config in feat_configs:
      if not feat_config['enabled']:
        continue

      if IsCNNFeat(feat_config['type']):
        # create params
        cur_params = CNNParams()
        cur_params.feat_name = feat_config['type'].encode("utf-8")
        print 'using feature: {}'.format(cur_params.feat_name)
        cur_params.feat_type = MapNameToFeatType(cur_params.feat_name)
        self.feat_params.append(cur_params)
        # create feature
        cnn_feat_computer = DeepCNNFeature()
        cnn_feat_computer.Init(cur_params)
        cnn_feat_computer.Start()
        self.feat_extractors.append(cnn_feat_computer)

    print "feature config loaded"

  def init_from_features(self, features):
    """Create extractor from custom features.

    Args:
      features: a list of custom defined feature extractors.
    """
    # add features.
    for feature in features:
      assert issubclass(
          type(feature), common.BaseFeatExtractor
      ), "feature extractor not a subclass of BaseFeatExtractor"
      self.feat_extractors[feature.feat_name] = feature

  def start(self):
    """Start all feature extractors.
    """
    for feature in self.feat_extractors.values():
      feature.start()

  def set_input(self, rgb_img):
    """Set image input.
    """
    for feature in self.feat_extractors.values():
      feature.set_input(rgb_img)

  def compute(self, rgb_img=None, mask=None):
    """Compute all features.

    Args:
      rgb_img: color input image.
      mask: image mask to select ROI.
    Returns:
      a dictionary of features.
    """
    feats = {}
    for feature in self.feat_extractors.values():
      cur_feat = feature.compute(rgb_img, mask)
      feats[feature.feat_name] = cur_feat
    return feats

  def compute_batch(self, rgb_imgs, masks=None):
    """Compute batch feature.
    """
    feats = {}
    for feature in self.feat_extractors.values():
      cur_feats = feature.compute_batch(rgb_imgs, masks)
      feats[feature.feat_name] = cur_feats
    return feats

  def calc_dist(self, feats1, feats2, weights=None):
    """Combined distance for feature sets.

    Args:
      feats1: feature set 1.
      feats2: feature set 2.
      weights: weight for each feature.
    Returns:
      final feature set distance.
    """
    total_dist = 0
    if weights is not None:
      assert len(weights) == len(
          feats1.keys), "inconsistent weight dimension with features"
    assert len(feats1.keys) == len(
        feats2.keys), "inconsistent feature set number"
    for feat_name in feats1.keys():
      total_dist += self.feat_extractors[feat_name].calc_dist(
          feats1[feat_name], feats2[feat_name])
    return total_dist


if __name__ == "__main__":
  pass
