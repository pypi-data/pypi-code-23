
from duckietown_swarm.dcache_wire import create_propose_message, \
    interpret_message, create_dismiss_message, create_signature_message

from comptests.registrar import run_module_tests, comptest


@comptest
def test_yaml_propose():
    buckets = ('one', 'two')
    data = 'mydata'
    validity_interval = (0, None)
    msg = create_propose_message(buckets=buckets, data=data, validity=validity_interval)
    s = interpret_message(msg)
    assert s.buckets == buckets, s.buckets
    assert s.validity == validity_interval, s
    assert s.data == data


@comptest
def test_yaml_propose2():
    buckets = 'thebucket'
    data = 'mydata'
    validity_interval = (0, None)
    msg = create_propose_message(buckets=buckets, data=data, validity=validity_interval)
    s = interpret_message(msg)
    assert s.buckets == (buckets,), s.buckets
    assert s.validity == validity_interval, s
    assert s.data == data


@comptest
def test_yaml_dismiss():
    buckets = ('one', 'two')
    data = 'mydata'
    validity_interval = (0, None)
    msg = create_dismiss_message(buckets=buckets, data=data, validity=validity_interval)
    s = interpret_message(msg)
    assert s.buckets == buckets, s.buckets
    assert s.validity == validity_interval, s
    assert s.data == data


@comptest
def test_yaml_signature():
    signer = 'me'
    data_hash = 'mydata'
    signature = 'signature'
    msg = create_signature_message(data_hash=data_hash, signer=signer, signature=signature)
    s = interpret_message(msg)
    assert s.signer == signer, s
    assert s.signature == signature, s
    assert s.data == data_hash


if __name__ == '__main__':
    run_module_tests()
