import datetime

import os
import pyarrow.parquet as pq
import pyarrow as pa
from diskcache import Cache
import pandas as pd

disk_cache = Cache('/tmp')


def __read_df(name: str) -> pd.DataFrame:
    path = __get_path(name)
    if not os.path.exists(path):
        return None

    table = pq.read_table(path)
    df = table.to_pandas()

    return df


def __write_df(df: pd.DataFrame, name: str):
    table = pa.Table.from_pandas(df)
    pq.write_table(table, __get_path(name))


def __get_path(name: str) -> str:
    return "/tmp/" + name + ".parquet"


def get(key: str, max_age=0):
    v = disk_cache.get(key, default=None)

    if v is None:
        return v

    max_age_timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()) - max_age

    if v["timestamp"] < max_age_timestamp:
        return None

    return v["value"]


def set(key: str, value: object) -> bool:
    value = {
        "timestamp": int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()),
        "value": value,
    }
    return disk_cache.set(key, value)


def clear() -> int:
    return disk_cache.clear()


def stats():
    return disk_cache.stats()