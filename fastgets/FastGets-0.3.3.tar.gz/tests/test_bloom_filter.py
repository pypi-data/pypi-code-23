
from fastgets.core.client import get_filter_client


def test_bloom_filter():
    get_filter_client().add('instance_id', 'http://www.baidu.com')
    assert get_filter_client().exists('instance_id', 'http://www.baidu.com')
    assert not get_filter_client().exists('instance_id', 'http://www.qq.com')
