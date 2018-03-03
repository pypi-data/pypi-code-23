"""Class to generate different types of color descriptors.
"""

import numpy as np
from sklearn.cluster import KMeans

import cv2

from owl.data import img_tools
from owl.features import common


class ColorParams(common.BaseFeatParams):
  """Color specific parameters.
  """
  pass


class ColorClusters(common.BaseFeatExtractor):
  """Color cluster descriptors.
  """
  # each element is a tuple of pixel value.
  color_palette = []

  def __init__(self, feat_params):
    super(ColorClusters, self).__init__(feat_params)
    self.feat_name = "color_cluster"
    self.feat_type = common.FeatType.COLOR_CLUSTER
    self.feat_params_ = feat_params

  def set_input(self, rgb_img):
    self.internal_img = np.float32(rgb_img)
    # convert to LAB.
    self.internal_img /= 255

  def compute(self, rgb_img=None, mask=None):
    # set input.
    if rgb_img is not None:
      self.set_input(rgb_img)
    # reshape img pixels.
    if mask is None:
      pixels = self.internal_img.reshape((-1, 3))
    else:
      imgw, imgh, _ = self.internal_img.shape
      # filter valid pixels.
      pixels = [
          self.internal_img[row, col]
          for row, col in zip(range(imgh), range(imgw)) if mask[row, col] > 0
      ]
    # do clustering.
    num_cluster = 8
    self.feat_dim = num_cluster * 4
    # sklearn kmeans
    #clr = KMeans(n_clusters=num_cluster)
    #clr.fit(pixels)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    # fit.
    _, labels, centers = cv2.kmeans(pixels, num_cluster, None, criteria, 10,
                                    cv2.KMEANS_PP_CENTERS)
    # compute weight.
    weights = np.zeros((num_cluster, 1), np.float32)
    for cls_id in labels:
      weights[cls_id] += 1
    weights /= len(pixels)
    # rank cluster centers based on weights from high to low.
    # order: (pixel, weight).
    weighted_cls = np.append(centers, weights, axis=1)
    sorted_cls = sorted(weighted_cls, key=lambda cls: cls[3], reverse=True)
    # form feature vector by concatenating weights and cluster centers.
    feat = []
    self.color_palette = []
    for cluster in sorted_cls:
      feat.extend([cluster[3], cluster[0], cluster[1], cluster[2]])
      self.color_palette.append((int(cluster[0] * 255), int(cluster[1] * 255),
                                 int(cluster[2] * 255)))
    feat = np.array(feat).reshape((1, -1))
    return feat

  def vis_clusters(self):
    """Visualize clusters and save to image.
    """
    num_cluster = len(self.color_palette)
    canvas = np.zeros((50, 51 * num_cluster, 3), np.uint8)
    for idx, cls_center in enumerate(self.color_palette):
      pt1 = (idx * 50, 0)
      pt2 = (idx * 50 + 50, 50)
      cv2.rectangle(canvas, pt1, pt2, cls_center, -1)
    img_tools.write_img_arr(canvas, "palette.png")

  def calc_dist(self, feat1, feat2):
    clusters1 = []
    clusters2 = []
    assert len(feat1) == len(
        feat2), "two features must have the same dimension"
    cls_num = len(feat1) / 4
    for i in range(cls_num):
      # first element is weight.
      cls1 = feat1[i * 4:i * 4 + 4]
      cls2 = feat2[i * 4:i * 4 + 4]
      clusters1.append(cls1)
      clusters2.append(cls2)
    # compute pairwise cluster distance.
    cls_dists = np.zeros((cls_num, cls_num), np.float32)
    for id1, cls1 in enumerate(clusters1):
      for id2, cls2 in enumerate(clusters2):
        cur_dist = np.linalg.norm(cls1[1:4] - cls2[1:4], 2)
        cur_dist = min(1, cur_dist / MAX_DIST)
        cls_dists[id1, id2] = (id2, cur_dist)
      # sort distance from low to high.
      cls_dists[id1] = sorted(
          cls_dists[id1], key=lambda dist_unit: dist_unit[1])
    # temporary weight values during composition.
    tempw1 = [cls[0] for cls in clusters1]
    tempw2 = [cls[0] for cls in clusters2]
    # cost to compose 1 (query) using 2 (db).
    dist12 = 0
    for id1 in range(cls_num):
      for id2 in range(cls_num):
        best_id = cls_dists[id1, id2][0]
        if tempw2[best_id] <= 0:
          continue
        to_fill_amount = min(tempw1[id1], tempw2[best_id])
        dist12 += cls_dists[id1, id2][1] * to_fill_amount
        # update weight.
        tempw1[id1] -= to_fill_amount
        tempw2[best_id] -= to_fill_amount
        if tempw1[id1] <= 0:
          break

    return dist12
