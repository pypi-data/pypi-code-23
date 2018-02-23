"""Simple object segmentation.
"""

import numpy as np

import cv2


class SimpleObjectSegmentor(object):
  """Class for simple segmentor.

  Segmentation for simple background.
  """

  def boundary_replicate_cut(self, img_rgb):
    """Apply graphcut on image with replicated boundary.

    Args:
      img_rgb: numpy array of rgb image.
    Returns:
      binary mask (uint8) with foreground set to 255.
    """
    # duplicate boundary pixel.
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    imgh, imgw, _ = img_bgr.shape
    padding = 20
    new_img = cv2.copyMakeBorder(img_bgr, padding, padding, padding, padding,
                                 cv2.BORDER_REPLICATE)
    # run graph cut.
    fg_mask = np.zeros((imgh + 2 * padding, imgw + 2 * padding), np.uint8)
    bgdmodel = np.zeros((1, 65), np.float64)
    fgdmodel = np.zeros((1, 65), np.float64)
    rect = (padding, padding, imgw, imgh)
    cv2.grabCut(new_img, fg_mask, rect, bgdmodel, fgdmodel, 3,
                cv2.GC_INIT_WITH_RECT)
    res_mask = cv2.bitwise_and(fg_mask, 1).astype("uint8")
    res_mask = res_mask[rect[1]:rect[3] + rect[1], rect[0]:rect[2] + rect[0]]
    return res_mask * 255

  def boundary_adapt_replicate_cut(self, img_rgb):
    """Replicate boundary for cut with most frequent pixel.

    Args:
      img_rgb: rgb image ndarray.
    Returns:
      binary mask.
    """
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    imgh, imgw, _ = img_bgr.shape
    # use most frequent boundary pixel.
    top_row = img_bgr[0, :, :]
    bottom_row = img_bgr[-1, :, :]
    left_col = img_bgr[:, 0, :]
    right_col = img_bgr[:, -1, :]
    boundary_pixels = np.vstack((top_row, bottom_row, left_col, right_col))
    boundary_pixels = boundary_pixels.astype(np.float32)
    term_crit = (cv2.TERM_CRITERIA_EPS, 30, 0.1)
    K = 5
    _, labels, centers = cv2.kmeans(boundary_pixels, K, term_crit, 5,
                                    cv2.KMEANS_PP_CENTERS)
    label_cnt = np.zeros((K), np.int32)
    for label in labels:
      label_cnt[label] += 1
    max_color = centers[np.argmax(label_cnt), :]
    max_color = [np.uint8(v) for v in max_color]
    padding = 20
    dst2 = np.zeros((imgh + 2 * padding, imgw + 2 * padding, 3), np.uint8)
    dst2[:] = max_color
    dst2[padding:padding + imgh, padding:padding + imgw, :] = img_bgr
    # perform cut.
    fg_mask = np.zeros((imgh + 2 * padding, imgw + 2 * padding), np.uint8)
    bgdmodel = np.zeros((1, 65), np.float64)
    fgdmodel = np.zeros((1, 65), np.float64)
    rect = (padding, padding, imgw, imgh)
    cv2.grabCut(dst2, fg_mask, rect, bgdmodel, fgdmodel, 3,
                cv2.GC_INIT_WITH_RECT)
    res_mask = cv2.bitwise_and(fg_mask, 1).astype("uint8")
    res_mask = res_mask[rect[1]:rect[3] + rect[1], rect[0]:rect[2] + rect[0]]
    return res_mask * 255

  def otsu(self, img_rgb):
    """Use OTSU method to do graph cut.
    """
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    imgh, imgw, _ = img_bgr.shape
    padding = 20
    dst = cv2.copyMakeBorder(img_bgr, padding, padding, padding, padding,
                             cv2.BORDER_REPLICATE)
    dst2_gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(dst2_gray, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((7, 7), np.uint8)
    closed_thresh = cv2.morphologyEx(
        thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    # cv2.imshow('closed_thresh', closed_thresh)
    # cv2.waitKey(wait_time)
    fg_mask = np.zeros((imgh + padding * 2, imgw + padding * 2, 1), np.uint8)
    fg_mask.fill(cv2.GC_BGD)
    fg_mask.ravel()[closed_thresh.ravel() == 255] = cv2.GC_PR_FGD
    # should we add PR_BGD?
    rect = (padding, padding, imgw, imgh)
    bgdmodel = np.zeros((1, 65), np.float64)
    fgdmodel = np.zeros((1, 65), np.float64)
    cv2.grabCut(dst, fg_mask, rect, bgdmodel, fgdmodel, 2,
                cv2.GC_INIT_WITH_MASK)
    res_mask = cv2.bitwise_and(fg_mask, 1).astype("uint8")
    res_mask = res_mask[rect[1]:rect[3] + rect[1], rect[0]:rect[2] + rect[0]]
    return res_mask * 255
