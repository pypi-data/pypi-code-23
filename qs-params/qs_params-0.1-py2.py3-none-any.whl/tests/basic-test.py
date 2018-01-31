
from qs import deserialize

def inc(x):
    return x + 1

def test_answer():
    assert inc(3) == 4

def test_deserialize():
    assert deserialize('hola=caracola&adios=caracol&foo=bar&nested.value=foobar') == {'hola':'caracola','adios':'caracol','foo':'bar','nested':{'value': 'foobar'}}
