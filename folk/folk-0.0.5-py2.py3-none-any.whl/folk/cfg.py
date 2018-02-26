"""Folk configuration."""

import functools

from birch import Birch


@functools.lru_cache(maxsize=2)
def folk_cfg():
    return Birch(
        namespace='folk',
        supported_formats=['json', 'yaml'],
    )


class CfgKey(object):
    MetricDbNames = "METRIC_DB_NAMES"
    MetricDbs = "METRIC_DBS"
    DbType = "TYPE"
