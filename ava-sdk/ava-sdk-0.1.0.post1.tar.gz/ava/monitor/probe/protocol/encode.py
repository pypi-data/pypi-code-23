# -*- coding: utf-8 -*-

"""
ProbeMetric decoder
(translated from https://github.com/qbox/base/blob/develop/qiniu/src/qiniu.com/probe/common/protocol/line/encode.go)

Example:

m = ProbeMetric()
m.measurement = 'test-metric'
m.time = time.time()
m.tagk_list = ['tagk1', 'tagk2']
m.tagv_list = ['tagv1', 'tagv2']
m.fieldk_list = ['field1', 'field 2']
m.fieldv_list = ['str1', 123]

# encoded string
test-metric,tagk1=tagv1,tagk2=tagv2 field1="str1",field\ 2=123 1495784747466488785
"""

import time
import metric


def encode(metric):
    """对metric进行编码

    Args:
            metric: type ProbeMetric

    Returns:
            string, encoded metric string
    """
    encoded_str_arr = []
    encoded_str_arr.append(encode_measurement(metric.measurement))
    encoded_str_arr.append(encode_tag_list(metric.tagk_list, metric.tagv_list))
    encoded_str_arr.append(' ')
    encoded_str_arr.append(encode_field_list(
        metric.fieldk_list, metric.fieldv_list))
    if metric.time != None:
        encoded_str_arr.append(' ')
        # convert to nano seconds
        encoded_str_arr.append('%d' % int(metric.time*1000000000))
    return ''.join(encoded_str_arr)


def _encode(raw, escape_code_kv):
    """使用自定义编码集，对字符串进行编码

    Args:
            raw: 原始数据，类型不确定
            escape_code_kv: 需要编码的字符串 -> 替换字符串 的map

    Returns:
            编码之后的字符串
    """
    encode_str_arr = []
    for b in str(raw):
        codev = escape_code_kv.get(b, b)
        encode_str_arr.append(codev)
    return ''.join(encode_str_arr)


def encode_measurement(measurement):
    escape_code_kv = {
        ',': '''\,''',
        ' ': '''\ ''',
    }
    return _encode(measurement, escape_code_kv)


def encode_tag_list(tagk_list, tagv_list):
    lenk, lenv = len(tagk_list), len(tagv_list)
    if lenk != lenv:
        # log TODO
        return ''
    encoded_str_arr = []
    for i in range(lenk):
        encoded_str_arr.append(',')
        encoded_str_arr.append(encode_tag(tagk_list[i]))
        encoded_str_arr.append('=')
        encoded_str_arr.append(encode_tag(tagv_list[i]))
    return ''.join(encoded_str_arr)


def encode_tag(tag):
    escape_code_kv = {
        ',': '''\,''',
        ' ': '''\ ''',
        '=': '''\=''',
    }
    return _encode(tag, escape_code_kv)


def encode_field(field):
    return encode_tag(field)


def encode_field_list(fieldk_list, fieldv_list):
    lenk, lenv = len(fieldk_list), len(fieldv_list)
    if lenk != lenv:
        # log TODO
        return ''
    encoded_str_arr = []
    first = True
    for i in range(lenk):
        if not first:
            encoded_str_arr.append(',')
        first = False
        encoded_str_arr.append(encode_field(fieldk_list[i]))
        encoded_str_arr.append('=')
        encoded_str_arr.append(encode_field_value(fieldv_list[i]))
    return ''.join(encoded_str_arr)


def encode_field_value(value):
    escape_code_kv = {
        ',': '''\,''',
        ' ': '''\ ''',
        '=': '''\=''',
        '"': '''\"''',
    }
    # 将各种类型的value，转换成string
    value_str = ''
    """
	坑：
		>>> b = True
		>>> isinstance(b, bool)
		True
		>>> isinstance(b, int)
		True
	"""
    if isinstance(value, bool):
        value_str = 'true' if value else 'false'
    elif isinstance(value, int):
        value_str = str(value)
    elif isinstance(value, float):
        value_str = str(value)
    elif isinstance(value, basestring):
        value_str = value

    encoded = _encode(value_str, escape_code_kv)
    if isinstance(value, basestring):
        return '"' + encoded + '"'
    else:
        return encoded
