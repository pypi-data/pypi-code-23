#! /usr/bin/env python3
"""
Implements a class for text detection on images. Adapted from:
Repo: https://github.com/argman/EAST
Commit: 26911bee9ed013a7a8ac64ea329a45a335528220
"""

import os
from typing import Any, Union

import tensorflow as tf
import numpy as np
import cv2  # pylint: disable=import-error

import eastdetector.model
import lanms


def _restore_rectangle(origin: np.array, geometry: np.array) -> np.array:
    # pylint: disable=invalid-name,too-many-locals
    """
    Taken from icdar.py in https://github.com/argman/EAST on 20.11.2017
    """
    d = geometry[:, :4]
    angle = geometry[:, 4]
    # for angle > 0
    origin_0 = origin[angle >= 0]
    d_0 = d[angle >= 0]
    angle_0 = angle[angle >= 0]
    if origin_0.shape[0] > 0:
        # yapf: disable
        p = np.array([np.zeros(d_0.shape[0]),
                      -d_0[:, 0] - d_0[:, 2],
                      d_0[:, 1] + d_0[:, 3],
                      -d_0[:, 0] - d_0[:, 2],
                      d_0[:, 1] + d_0[:, 3],
                      np.zeros(d_0.shape[0]),
                      np.zeros(d_0.shape[0]),
                      np.zeros(d_0.shape[0]),
                      d_0[:, 3], -d_0[:, 2]])

        p = p.transpose((1, 0)).reshape((-1, 5, 2))  # N*5*2

        rotate_matrix_x = np.array([np.cos(angle_0), np.sin(angle_0)]).transpose((1, 0))
        rotate_matrix_x = np.repeat(rotate_matrix_x, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))  # N*5*2

        rotate_matrix_y = np.array([-np.sin(angle_0), np.cos(angle_0)]).transpose((1, 0))
        rotate_matrix_y = np.repeat(rotate_matrix_y, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))

        p_rotate_x = np.sum(rotate_matrix_x * p, axis=2)[:, :, np.newaxis]  # N*5*1
        p_rotate_y = np.sum(rotate_matrix_y * p, axis=2)[:, :, np.newaxis]  # N*5*1

        p_rotate = np.concatenate([p_rotate_x, p_rotate_y], axis=2)  # N*5*2

        p3_in_origin = origin_0 - p_rotate[:, 4, :]
        new_p0 = p_rotate[:, 0, :] + p3_in_origin  # N*2
        new_p1 = p_rotate[:, 1, :] + p3_in_origin
        new_p2 = p_rotate[:, 2, :] + p3_in_origin
        new_p3 = p_rotate[:, 3, :] + p3_in_origin

        new_p_0 = np.concatenate([new_p0[:, np.newaxis, :], new_p1[:, np.newaxis, :],
                                  new_p2[:, np.newaxis, :], new_p3[:, np.newaxis, :]], axis=1)  # N*4*2
        # yapf: enable
    else:
        new_p_0 = np.zeros((0, 4, 2))
    # for angle < 0
    origin_1 = origin[angle < 0]
    d_1 = d[angle < 0]
    angle_1 = angle[angle < 0]
    if origin_1.shape[0] > 0:
        # yapf: disable
        p = np.array([-d_1[:, 1] - d_1[:, 3],
                      -d_1[:, 0] - d_1[:, 2],
                      np.zeros(d_1.shape[0]),
                      -d_1[:, 0] - d_1[:, 2],
                      np.zeros(d_1.shape[0]),
                      np.zeros(d_1.shape[0]),
                      -d_1[:, 1] - d_1[:, 3],
                      np.zeros(d_1.shape[0]),
                      -d_1[:, 1], -d_1[:, 2]])
        p = p.transpose((1, 0)).reshape((-1, 5, 2))  # N*5*2

        rotate_matrix_x = np.array([np.cos(-angle_1), -np.sin(-angle_1)]).transpose((1, 0))
        rotate_matrix_x = np.repeat(rotate_matrix_x, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))  # N*5*2

        rotate_matrix_y = np.array([np.sin(-angle_1), np.cos(-angle_1)]).transpose((1, 0))
        rotate_matrix_y = np.repeat(rotate_matrix_y, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))

        p_rotate_x = np.sum(rotate_matrix_x * p, axis=2)[:, :, np.newaxis]  # N*5*1
        p_rotate_y = np.sum(rotate_matrix_y * p, axis=2)[:, :, np.newaxis]  # N*5*1

        p_rotate = np.concatenate([p_rotate_x, p_rotate_y], axis=2)  # N*5*2

        p3_in_origin = origin_1 - p_rotate[:, 4, :]
        new_p0 = p_rotate[:, 0, :] + p3_in_origin  # N*2
        new_p1 = p_rotate[:, 1, :] + p3_in_origin
        new_p2 = p_rotate[:, 2, :] + p3_in_origin
        new_p3 = p_rotate[:, 3, :] + p3_in_origin

        new_p_1 = np.concatenate([new_p0[:, np.newaxis, :], new_p1[:, np.newaxis, :],
                                  new_p2[:, np.newaxis, :], new_p3[:, np.newaxis, :]], axis=1)  # N*4*2
        # yapf: enable
    else:
        new_p_1 = np.zeros((0, 4, 2))
    return np.concatenate([new_p_0, new_p_1])


def _resize_image(image: np.ndarray, max_side_len: int = 2400) -> Any:
    """
    Resize image to a size multiple of 32 which is required by the network.
    :param image: the resized image
    :param max_side_len: limit of max image size to avoid out of memory in gpu
    :return: the resized image and the resize ratio
    """
    h, w, _ = image.shape  # pylint: disable=invalid-name

    resize_w = w
    resize_h = h

    # limit the max side
    if max(resize_h, resize_w) > max_side_len:
        ratio = float(max_side_len) / resize_h if resize_h > resize_w else float(max_side_len) / resize_w
    else:
        ratio = 1.
    resize_h = int(resize_h * ratio)
    resize_w = int(resize_w * ratio)

    if min([resize_w, resize_h]) < 64:
        resize_h = resize_h if resize_h % 32 == 0 else (resize_h // 32 + 1) * 32
        resize_w = resize_w if resize_w % 32 == 0 else (resize_w // 32 + 1) * 32
    else:
        resize_h = resize_h if resize_h % 32 == 0 else (resize_h // 32 - 1) * 32
        resize_w = resize_w if resize_w % 32 == 0 else (resize_w // 32 - 1) * 32
    image_resized = cv2.resize(image, (int(resize_w), int(resize_h)))

    ratio_h = resize_h / float(h)
    ratio_w = resize_w / float(w)

    return image_resized, (ratio_h, ratio_w)


class TextDetectorParams:
    """
    Parameter class
    """
    threshold_score_map = 0.8
    threshold_nms = 0.2


class TextDetector:
    """
    Detects text with the NN proposed by "EAST: An Efficient and Accurate Scene Text Detector".
    Adapted from: see top
    """

    def __init__(self, checkpoint_path: str):
        tf.logging.set_verbosity(tf.logging.ERROR)

        self.__closed = False

        checkpoint_state = tf.train.get_checkpoint_state(checkpoint_path)

        if checkpoint_state is None:
            raise RuntimeError("Failed to read the tensorflow checkpoint path from: {!r}".format(checkpoint_path))

        model_path = os.path.join(checkpoint_path, os.path.basename(checkpoint_state.model_checkpoint_path))  # pylint: disable=no-member

        self.__input_image = tf.placeholder(np.float32, shape=[None, None, None, 3], name='input_image')
        self.__f_score, self.__f_geometry = eastdetector.model.model(self.__input_image, is_training=False)

        self.__session = tf.Session()
        global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)
        variable_averages = tf.train.ExponentialMovingAverage(0.997, global_step)
        saver = tf.train.Saver(variable_averages.variables_to_restore())
        saver.restore(self.__session, model_path)

    def __enter__(self):
        if self.__closed:
            raise RuntimeError("TextDetector: Session has already been closed.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        # pylint: disable=missing-docstring
        self.__session.close()
        self.__closed = True

    def detect(self, image: np.ndarray, params=TextDetectorParams()) -> Union[None, np.ndarray]:
        """
        Detector method.
        :param image:
        :param params:
        :return: An (N x 4 x 2) array, where N is the amount of boxes found and the (4 x 2) subarray holds the corner
                 points.
        """
        if self.__closed:
            raise RuntimeError("TextDetector: Session has already been closed.")
        image_resized, (ratio_h, ratio_w) = _resize_image(image)

        score_map, geo_map = self.__session.run(
            [self.__f_score, self.__f_geometry], feed_dict={self.__input_image: [image_resized]})
        if len(score_map.shape) == 4:
            score_map = score_map[0, :, :, 0]
            geo_map = geo_map[0, :, :, ]

        xy_text = np.argwhere(score_map > params.threshold_score_map)  # filter the score map
        xy_text = xy_text[np.argsort(xy_text[:, 0])]  # sort the text boxes via the y axis
        text_box_restored = _restore_rectangle(xy_text[:, ::-1] * 4, geo_map[xy_text[:, 0], xy_text[:, 1], :])

        boxes = np.zeros((text_box_restored.shape[0], 9), dtype=np.float32)
        boxes[:, :8] = text_box_restored.reshape((-1, 8))
        boxes[:, 8] = score_map[xy_text[:, 0], xy_text[:, 1]]

        boxes = lanms.merge_quadrangle_n9(boxes.astype(np.float32), params.threshold_nms)

        if boxes.shape[0] == 0:
            return None
        box_thresh = 0.1
        boxes = boxes[boxes[:, 8] > box_thresh]

        if boxes.shape[0] == 0:
            return None

        boxes = boxes[:, :8].reshape((-1, 4, 2))
        boxes[:, :, 0] /= ratio_w
        boxes[:, :, 1] /= ratio_h

        return boxes
