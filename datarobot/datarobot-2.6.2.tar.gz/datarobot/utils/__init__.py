"""This module is not considered part of the public interface. As of 2.3, anything here
may change or be removed without warning."""

import re
from datetime import datetime, date

import pandas as pd
import six
from dateutil import parser, tz

from .deprecation import deprecated, deprecation_warning  # noqa
from .sourcedata import is_urlsource, recognize_sourcedata, dataframe_to_buffer  # noqa

ALL_CAPITAL = re.compile(r'(.)([A-Z][a-z]+)')
CASE_SWITCH = re.compile(r'([a-z0-9])([A-Z])')
UNDERSCORES = re.compile(r'[a-z]_[a-z]{0,1}')


def underscorize(value):
    partial_result = ALL_CAPITAL.sub(r'\1_\2', value)
    return CASE_SWITCH.sub(r'\1_\2', partial_result).lower()


def underscoreToCamel(match):
    groups = match.group()
    if len(groups) == 2:
        # underscoreToCamel('sample_pct__gte') -> 'samplePct__gte'
        return groups
    return groups[0] + groups[2].upper()


def camelize(value):
    return UNDERSCORES.sub(underscoreToCamel, value)


def from_api(data, do_recursive=True):
    if type(data) not in (dict, list):
        return data
    if isinstance(data, list):
        return _from_api_list(data, do_recursive=do_recursive)
    return _from_api_dict(data, do_recursive=do_recursive)


def _from_api_dict(data, do_recursive=True):
    app_data = {}
    for k, v in six.iteritems(data):
        if v is None:
            continue
        app_data[underscorize(k)] = from_api(v, do_recursive=do_recursive) if do_recursive else v
    return app_data


def _from_api_list(data, do_recursive=True):
    return [from_api(datum, do_recursive=do_recursive) for datum in data]


def remove_empty_keys(metadata):
    return {k: v for k, v in metadata.items() if v is not None}


def parse_time(time_str):
    try:
        return parser.parse(time_str, tzinfos={'UTC': tz.tzutc()})
    except Exception:
        return time_str


def datetime_to_string(datetime_obj):
    """ Converts to isoformat after dropping microseconds
    """
    if not isinstance(datetime_obj, datetime):
        msg = 'expected to be passed a datetime.datetime, was passed {}'.format(type(datetime_obj))
        raise ValueError(msg)
    stripped = datetime_obj.replace(microsecond=0)
    return stripped.isoformat()


def to_api(data):
    """
    :param data: dictionary {'max_digits': 1}
    :return: {'maxDigits': 1}
    """
    if not data:
        return {}
    assert isinstance(data, dict), 'Wrong type'
    return _to_api_item(data)


def _to_api_item(item):
    if isinstance(item, dict):
        dense_item = remove_empty_keys(item)
        return {camelize(k): _to_api_item(v) for k, v in six.iteritems(dense_item)}
    elif isinstance(item, list):
        return [_to_api_item(subitem) for subitem in item]
    elif isinstance(item, datetime):
        return datetime_to_string(item)
    elif isinstance(item, date):
        return item.isoformat()
    else:
        return item


def get_id_from_response(response):
    location_string = response.headers['Location']
    return get_id_from_location(location_string)


def get_id_from_location(location_string):
    return location_string.split('/')[-2]


def get_duplicate_features(features):
    duplicate_features = set()
    seen_features = set()
    for feature in features:
        if feature in seen_features:
            duplicate_features.add(feature)
        else:
            seen_features.add(feature)
    return list(duplicate_features)


def raw_prediction_response_to_dataframe(pred_response):
    """Raw predictions for classification come as nested json objects.

    This will extract it to be a single dataframe.

    Parameters
    ----------
    pred_response : dict
        The loaded json object returned from the prediction route.

    Returns
    -------
    frame : pandas.DataFrame

    """
    predictions = from_api(pred_response)['predictions']
    frame = pd.DataFrame.from_records(predictions)
    return frame


def encode_utf8_if_py2(string):
    """__repr__ is supposed to return string (bytes) in 2 and string (unicode) in 3
    this function can be used to convert our unicode to strings in Python 2 but leave them alone
    in Python 3"""
    return string.encode('utf-8') if six.PY2 else string
