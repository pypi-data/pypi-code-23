"""Metric databases for folk."""

import abc
import warnings
from datetime import datetime
from importlib import import_module

from decore import lazy_property
from strct.dicts import safe_nested_val

from .cfg import (
    folk_cfg,
    CfgKey,
)
from .exceptions import (
    FolkMissingConfigurationValueError,
)


class MetricKey(object):
    # folk-specific parameters
    MODEL_ID = 'model_identifier'
    RUN_ID = 'run_id'
    RUN_AT = 'run_at'
    # general ML parameters
    LBL_COL = 'lbl_col'
    DATASET_SIZE = 'dataset_size'
    N_FOLDS = 'n_folds'
    N_CLASS = 'n_classes'
    ACC_MEAN = 'accuracy_mean'
    ACC_STD = 'accuracy_std'


class FolkMetricsDB(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write_experiment_res(self, run_id=None, **kwargs):
        """Writes the result of a single experiment to the database.

        Parameters
        ----------
        res_doc : dict
            A key-value mapping of parameters and their values.
        run_id : str, optional
            A string identifier for the run this experiment is part of.
        """
        pass  # pragma: no cover


class FolkMetricsMongoDB(FolkMetricsDB):

    _ERR = "Missing config value for {} for MongoDB-based {} folk metrics db."

    """A MongoDB-based folk metrics database.

    Parameters
    ----------
    db_cfg : dict
        A mapping of db configuration parameters to their values.
    """
    def __init__(self, name, db_cfg):
        self.name = name
        for cfg_param in ['URI', 'DB_NAME', 'COLLECTION_NAME']:
            try:
                setattr(self, cfg_param.lower(), db_cfg[cfg_param])
            except KeyError:
                raise FolkMissingConfigurationValueError(
                    FolkMetricsMongoDB._ERR.format(cfg_param, self.name))
        self.collection = None

    @staticmethod
    @lazy_property
    def _mongo_client_cls():
        pymongo = import_module('pymongo')
        submodule = getattr(pymongo, 'mongo_client')
        return getattr(submodule, 'MongoClient')

    def get_collection(self):
        if self.collection is None:
            MongoClient = FolkMetricsMongoDB._mongo_client_cls()
            client = MongoClient(self.uri)
            db = client[self.db_name]
            self.collection = db[self.collection_name]
        return self.collection

    def write_experiment_res(self, res_doc, run_id=None):
        run_at = datetime.utcnow()
        if run_id is None:
            run_id = str(run_at.timestamp()).replace('.', '')
        col_obj = self.get_collection()
        col_obj.insert_one({
            MetricKey.RUN_ID: run_id,
            MetricKey.RUN_AT: run_at,
            **res_doc,
        })


TYPE_TO_CLS_MAP = {
    'mongodb': FolkMetricsMongoDB,
}


NAME_TO_DB_MAP = {}


def populate_name_to_db_map():
    cfg = folk_cfg()
    names_str = cfg.get(CfgKey.MetricDbNames, None)
    if names_str is None:
        return
    for name in names_str.split(','):
        db_cfg = safe_nested_val(
            key_tuple=(CfgKey.MetricDbs, name),
            dict_obj=cfg,
            default_value=None,
        )
        if db_cfg is None:
            warnings.warn(
                "Folk: No configuration for db {} included in {}.".format(
                    name, CfgKey.MetricDbs))
            continue
        try:
            db_type = db_cfg[CfgKey.DbType]
        except KeyError:
            warnings.warn("Folk: No type configured for db {}.".format(name))
            continue
        try:
            db_cls = TYPE_TO_CLS_MAP[db_type.lower()]
        except KeyError:
            warnings.warn("Folk: Unkown type configured for db {}.".format(
                name))
            continue
        db_instance = db_cls(name=name, db_cfg=db_cfg)
        NAME_TO_DB_MAP[name] = db_instance


populate_name_to_db_map()


def write_experiment_res(res_doc, db_name, run_id=None):
    """Writes an experiment results document to a folk metrics database.

    Parameters
    ----------
    res_doc : dict
        A key-value mapping of parameters and their values.
    db_name : str
        The name of the folk metrics db to write to. A db with this name must
        be configured for folk.
    run_id : str, optional
        A string identifier for the run this experiment is part of.
    """
    try:
        db_obj = NAME_TO_DB_MAP[db_name]
    except KeyError:
        warnings.warn((
            "Folk: No intact configuration for db {}. "
            "Results were not written to db.").format(db_name))
        return
    db_obj.write_experiment_res(res_doc=res_doc, run_id=run_id)
