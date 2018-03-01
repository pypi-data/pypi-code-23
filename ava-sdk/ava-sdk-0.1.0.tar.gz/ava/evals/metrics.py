#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import numpy as np
from sklearn.metrics import average_precision_score

from ava.log.logger import logger

IOU_THRESHOLD = 0.5


def calculate_metric(eval_file, classes, problem, acc_topn=[1]):
    """计算评估的统计值

    Args:
        eval_file   : 评估结果文件
        classes     : 分类名称 list
        problem     : 问题类型
        acc_topn    : 准确率的 topn list, 例如：[1, 3]，表示计算 top1, top3 的准确率

    Returns:
        dict()      : 返回的 metric dict，key list:
            top<n>_acc
            map
    """
    ret = dict()
    y_true, probas_pred = rank(eval_file, classes)
    if problem == "classification":
        for topn in acc_topn:
            acc = calculate_acc(classes, y_true, probas_pred, topn)
            ret["top%d_acc" % (topn)] = acc
    elif problem == "detection":
        ret["map"] = calculate_mean_ap(classes, y_true, probas_pred)

    return ret


def calculate_mean_ap(classes, y_true, probas_pred):
    nclasses = len(classes)
    ap = 0.0
    if nclasses == 0:
        return ap
    for i, v in enumerate(classes):
        y, p = y_true[:, i], probas_pred[:, i]
        # source 过滤？
        ap += average_precision_score(y, p)
    return ap / nclasses


def calculate_acc(classes, y_true, probas_pred, topn=1):
    nclasses, ny_true, nprobas_pred = len(
        classes), len(y_true), len(probas_pred)
    if nclasses == 0:
        raise Exception("class len is 0")
    if ny_true == 0 or nprobas_pred == 0:
        raise Exception("y_true of probas_pred len is 0")
    if ny_true != nprobas_pred:
        raise Exception("y_true len[%d] != probas_pred len[%d]" % (
            ny_ture, nprobas_pred))
    if topn > nclasses:
        raise Exception("topn[%d] > nclass[%d]" % (topn, nclasses))
    nsample = ny_true

    correct = 0.0
    for i in xrange(nsample):
        gt = np.array(y_true[i])         # example: [0, 0, 1, 0, 0]
        score = np.array(probas_pred[i])  # example: [0.1, 0.2, 0.9, 0.01, 0.7]
        ngt, nscore = len(gt), len(score)
        if ngt != nscore or ngt != nclasses:
            logger.debug(
                "length of gt[%d], score[%d], and class[%d] are not the same", ngt, nscore, nclasses)
            continue
        sorted_idx = np.argsort(score)[::-1]  # from max score to min score
        for j in xrange(topn):
            if gt[sorted_idx[j]] == 1:
                correct += 1
                break
    return correct / nsample


def rank(filepath, classes):
    '''Caculate ground_truth and score of all samples in file.
    '''
    nclasses = len(classes)
    y_true = np.array([]).reshape(0, nclasses)
    probas_pred = np.array([]).reshape(0, nclasses)

    with open(filepath) as f:
        for line in f:
            label = json.loads(line).get('label')
            if not label:
                continue

            # first problem type only
            data = label[0].get('data')
            if not data:
                continue

            problem = label[0].get('type')

            gt = []
            pred = []
            if problem == 'classification':
                gt, pred = rank_classification(classes, data)
            elif problem == 'detection':
                gt, pred = rank_detection(classes, data)

            if len(gt) == nclasses and len(pred) == nclasses:
                y_true = np.append(y_true, [gt], axis=0)
                probas_pred = np.append(probas_pred, [pred], axis=0)
            else:
                logger.info('missing labels of line: ' + line)
                continue
    return y_true, probas_pred


def rank_classification(classes, data):
    '''Caculate ground_truth and score for classification of one sample.
    '''
    gt = []
    pred = []
    for i in classes:
        for j in data:
            if j.get('ground_truth') or not j.get('score'):
                gt.append(1 if j.get('class') == i else 0)
            elif j.get('score') and j.get('class') == i:
                pred.append(j.get('score'))
    return gt, pred


def rank_detection(classes, data):
    '''Caculate ground_truth and score for detection of one sample.
    '''
    gt = []
    pred = []
    for i in classes:
        y_bbox = []
        p_bbox = []
        for j in data:
            if (j.get('ground_truth') or not j.get('score')) and j.get('class') == i:
                y_bbox.append(j.get('bbox'))
            elif j.get('score') and j.get('class') == i:
                p_bbox.append((j.get('bbox'), j.get('score')))

        if not p_bbox:
            continue

        max_iou = 0
        score = 0
        for pbox in p_bbox:
            for ybox in y_bbox:
                iou = bb_iou(ybox, pbox[0])
                # if iou is negative, leave iou & score as zero
                if iou > max_iou:
                    max_iou = iou
                    score = pbox[1]

        gt.append(1 if max_iou >= IOU_THRESHOLD else 0)
        pred.append(score)

    return gt, pred


def bb_iou(a, b):
    '''Caculate intersection over union between two bbox.
    '''
    xA = max(a[0][0], b[0][0])
    xB = min(a[1][0], b[1][0])
    yA = max(a[1][1], b[1][1])
    yB = min(a[2][1], b[2][1])
    if xB - xA < 0 or yB - yA < 0:
        return 0
    inter = (xB - xA) * (yB - yA)
    boxa = (a[1][0] - a[0][0]) * (a[2][1] - a[1][1])
    boxb = (b[1][0] - b[0][0]) * (b[2][1] - b[1][1])
    return inter / float(boxa + boxb - inter)
