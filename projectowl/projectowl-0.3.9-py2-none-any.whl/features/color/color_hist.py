"""Color histogram.
"""

import numpy as np
import cv2

from owl.features import common


class ColorHistParams(common.BaseFeatParams):
  feat_type = common.FeatType.COLOR_HIST_LINEAR
  bin_nums = [16, 16, 16]
  color_space = common.ColorSpace.RGB


class ColorHistogram(common.BaseFeatExtractor):
  """Color histogram descriptors.
  """
  # separate color range for each channel.
  ch_color_ranges = []
  # concatenated color range.
  concat_color_range = []

  def __init__(self, feat_params):
    self.feat_name = "color_histogram"
    self.feat_type = feat_params.feat_type
    self.feat_params_ = feat_params

  def set_input(self, rgb_img):
    if self.feat_params_.color_space == common.ColorSpace.RGB:
      self.internal_img = rgb_img
      self.ch_color_ranges = [[0, 256], [0, 256], [0, 256]]
      self.concat_color_range = [0, 256, 0, 256, 0, 256]
    if self.feat_params_.color_space == common.ColorSpace.HSV:
      new_img = np.float32(rgb_img)
      new_img /= 255
      self.internal_img = cv2.cvtColor(new_img, cv2.COLOR_RGB2HSV)
      self.ch_color_ranges = [[0, 360], [0, 1], [0, 1]]
      self.concat_color_range = [0, 360, 0, 1, 0, 1]
    if self.feat_params_.color_space == common.ColorSpace.LAB:
      new_img = np.float32(rgb_img)
      new_img /= 255
      self.internal_img = cv2.cvtColor(new_img, cv2.COLOR_RGB2LAB)
      self.ch_color_ranges = [[0, 100], [-127, 127], [-127, 127]]
      self.concat_color_range = [0, 100, -127, 127, -127, 127]

  def compute(self, rgb_img=None, mask=None):
    if rgb_img is not None:
      self.set_input(rgb_img)
    num_pixels = self.internal_img.size / 3
    if mask is not None:
      rgb_img = cv2.resize(rgb_img, (mask.shape[1], mask.shape[0]))
    feat = None
    if self.feat_type == common.FeatType.COLOR_HIST_LINEAR:
      feat = None
      for ch_id in range(3):
        hist = cv2.calcHist([self.internal_img], [ch_id], mask,
                            [self.feat_params_.bin_nums[ch_id]],
                            self.ch_color_ranges[ch_id])
        hist = np.float32(hist) / num_pixels
        if feat is None:
          feat = hist
        else:
          feat = np.append(feat, hist, axis=0)
      feat = feat.flatten()
    if self.feat_type == common.FeatType.COLOR_HIST_JOINT:
      hist = cv2.calcHist([self.internal_img], [0, 1, 2], mask,
                          self.feat_params_.bin_nums, self.concat_color_range)
      hist = np.float32(hist) / num_pixels
      feat = hist.flatten()
    return feat

  def calc_dist(self, feat1, feat2):
    return np.linalg.norm(feat1 - feat2)

  def get_feat_dim(self):
    if self.feat_params_.feat_type == common.FeatType.COLOR_HIST_LINEAR:
      return sum(self.feat_params_.bin_nums)
    else:
      dim = 1
      for bin_num in self.feat_params_.bin_nums:
        dim *= bin_num
      return dim
