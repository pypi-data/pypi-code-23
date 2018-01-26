import pandas as pd
import numpy as np
import more_itertools
import datetime


def parse(raw_response):
    report = raw_response["report"]
    raw_data = report["data"]

    dimensions, metrics = _parse_header(report)
    data = _parse_data(raw_data, metric_count=len(metrics))
    header = _fix_header(dimensions, metrics, data)
    return pd.DataFrame(data, columns=header)


def _parse_header(report):
    dimensions = [_classification_or_name(dimension) for dimension in report["elements"]]
    metrics = [metric["name"] for metric in report["metrics"]]
    return dimensions, metrics


def _classification_or_name(element):
    if "classification" in element:
        return element["classification"]
    return element["name"]


def _parse_data(data, metric_count):
    """
    Recursive parsing of the "data" part of the Adobe response.
    :param data: list of dicts and lists. quite a complicated structure
    :param metric_count: int, number of metrics in report
    :return: list of lists
    """
    if len(data) > 0 and "breakdown" in data[0]:
        rows = list()
        for chunk in data:
            dim_value = _dimension_value(chunk)
            rows += [[dim_value] + row
                     for row in _parse_data(chunk["breakdown"], metric_count)]
        return rows
    else:
        return _parse_most_granular(data, metric_count)


def _parse_most_granular(data, metric_count):
    """
    Parsing of the most granular part of the response.
    It is different depending on if there's a granularity breakdown or not
    :param data: dict
    :param metric_count: int, number of metrics in report
    :return: list of lists
    """
    rows = list()
    for chunk in data:
        part_rows = [(val if val != "" else np.nan) for val in chunk["counts"]]
        # data alignment is a bit different if adding granularity breakdowns
        if len(chunk["counts"]) > metric_count:
            part_rows = more_itertools.chunked(iterable=part_rows, n=metric_count + 1)
        else:
            part_rows = [part_rows]

        dim_value = _dimension_value(chunk)
        rows += [[dim_value] + part_row for part_row in part_rows]
    return rows


def _dimension_value(chunk):
    if _dimension_value_is_nan(chunk):
        return np.nan
    elif "year" in chunk:
        return _to_datetime(chunk)
    else:
        return chunk["name"]


def _dimension_value_is_nan(chunk):
    return ("name" not in chunk) or (chunk["name"] == "") or (chunk["name"] == "::unspecified::")


def _to_datetime(chunk):
    time_stamp = datetime.datetime(
        year=chunk["year"],
        month=chunk["month"],
        day=chunk["day"],
        hour=chunk.get("hour", 0)
    )
    return time_stamp.strftime("%Y-%m-%d %H:00:00")


def _fix_header(dimensions, metrics, data):
    header = dimensions + metrics
    if len(header) != len(data[0]):  # can only be when granularity breakdown is used
        return ["Datetime"] + header
    return header
