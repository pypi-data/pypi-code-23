#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from ava.log.logger import initialize_test_logger
from ava.evals import metrics as eval_metrics


def test_calculate_acc():
    classes = ["a", "b", "c"]
    y_true = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 0],
    ]
    probas_pred = [
        [0.9, 0, 0],
        [0.1, 0.8, 0.3],
        [0.9, 0.2, 0.3],
        [0.8, 0.5, 0.1],
    ]

    acc = eval_metrics.calculate_acc(classes, y_true, probas_pred)
    assert(acc == 0.75)
    acc = eval_metrics.calculate_acc(classes, y_true, probas_pred, topn=2)
    assert(acc == 1.0)
