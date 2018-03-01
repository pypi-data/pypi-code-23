"""Shared testing resources for folk."""

import functools

import pandas as pd
from sklearn.linear_model import LogisticRegression

import pdpipe as pdp
from birch import Birch
from pymongo import MongoClient
from skutil.model_selection import ConstrainedParameterGrid

from folk import (
    ConstrainedParameterizedModel,
    ParameterizedPipeline,
)
from folk.cfg import CfgKey


# === Constants ===

def _model_getter(penalty, C, **kwargs):
    return LogisticRegression(penalty=penalty, C=C)


MODEL_PGRID = ConstrainedParameterGrid({
    'penalty': ['l1', 'l2'],
    'C': [0.3, 0.6, 0.9],
})


PMODEL = ConstrainedParameterizedModel(
    model_getter=_model_getter,
    param_grid=MODEL_PGRID,
)


def _pipeline_getter(lower=False, **kwargs):
    stages = [
        pdp.ColRename({'shleem_count': 'scount'}),
    ]
    if lower:
        stages.append(pdp.ApplyByCols('rank', str.lower))
    stages.append(pdp.ColDrop(columns='id'))
    return pdp.Pipeline(stages)


PIPE_PGRID = ConstrainedParameterGrid({
    'lower': [True, False],
    'lbl_col': ['rank'],
})


PPIPELINE = ParameterizedPipeline(
    pipeline_getter=_pipeline_getter,
    param_grid=PIPE_PGRID,
)

TEST_METRICS_DB = 'FOLK_TEST'


def _test_df():
    return pd.DataFrame(
        data=[
            [23, 'A', 4.3, 'e2f'],
            [43, 'C', 3.5, '2eqef'],
            [80, 'B', 8.8, 'isudgv'],
            [13, 'A', 3.6, '239u8h'],
            [77, 'B', 5.0, 'ds9h77'],
            [103, 'B', 5.5, '9hudsg'],
            [33, 'C', 2.2, '3t782'],
            [42, 'C', 3.66, 'dh2u'],
        ],
        index=[0, 1, 2, 3, 4, 5, 6, 7],
        columns=['shleem_count', 'rank', 'hizzard_ratio', 'id'],
    )


@functools.lru_cache(maxsize=1)
def _metrics_collection():
    folk_cfg = Birch('folk')
    db_cfg = folk_cfg[CfgKey.MetricDbs][TEST_METRICS_DB]
    client = MongoClient(db_cfg['URI'])
    metrics_collection = client[db_cfg['DB_NAME']][db_cfg['COLLECTION_NAME']]
    return metrics_collection


def _clean_db():
    metrics_collection = _metrics_collection()
    metrics_collection.delete_many({})
    assert metrics_collection.count({}) == 0
