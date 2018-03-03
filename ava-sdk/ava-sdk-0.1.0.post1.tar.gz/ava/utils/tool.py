# -*- coding: utf-8 -*-

import os
import math
import csv

from PIL import Image
import numpy as np
import cv2

from ava.utils.fetcher import Fetcher


def chunk(lst, size):
    """
    divide a list into several chunks with chunk `size`
    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def divide_list(lst, chunk_n):
    """
    divide a list into `chunk_n` chunks
    """
    if chunk_n == 0:
        return []

    if not lst:
        return [[]] * chunk_n

    result = chunk(lst, int(math.ceil(1.0 * len(lst) / chunk_n)))
    if len(result) < chunk_n:
        result = result + [[]] * (chunk_n - len(result))
    return result


def probe_img_format(uri):
    """
    probe image format from path or url
    """
    if os.path.exist(uri):
        img = open(uri, 'rb')
        header = img.read(32)
        img.close()
    else:
        res, err = Fetcher().fetch(uri)
        assert err is None, "test image format failed, fetch image error: %s" % str(
            err)
        header = res.body[:32]
    return test_jpeg(header) or test_exif(header) or test_png(header)


def test_jpeg(header):
    """JPEG data in JFIF format"""
    if header[6:10] == 'JFIF':
        return 'jpeg'


def test_exif(header):
    """JPEG data in Exif format"""
    if header[6:10] == 'Exif':
        return 'jpeg'


def test_png(header):
    """test PNG data"""
    if header[:8] == "\211PNG\r\n\032\n":
        return 'png'


def check_image_by_decode(image_bytes):
    """ check if image is valid by imdecode function from cv2 """
    try:
        np_string = np.fromstring(image_bytes, np.uint8)
        img_np = cv2.imdecode(np_string, 1)
        assert img_np is not None, 'decode result is None'
        return True, None, img_np
    except Exception as err:
        return False, err, None


def check_image_by_open(file_path):
    """ check if image is valid by open function from Pillow """
    try:
        img_np = Image.open(file_path)
        img_np = np.array(img_np, dtype=np.uint8)
        assert len(img_np.shape) == 3, 'incorrect image shape, shape: %d' % len(
            img_np.shape)
        assert img_np.shape[2] == 3, 'incorrect image channel, channel: %d' % img_np.shape[2]
        return True, None, img_np
    except Exception as err:
        return False, err, None


def merge_dicts(*dict_args):
    """
    merge a list of dict in to a new dict
    """
    result = {}
    for dictionary in dict_args:
        if dictionary is not None:
            result.update(dictionary)
    return result
