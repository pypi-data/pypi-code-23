
from qs import deserialize

def test_deserialize():
    assert deserialize('hola=caracola&adios=caracol&foo=bar&nested.value=foobar') == {'hola':'caracola','adios':'caracol','foo':'bar','nested':{'value': 'foobar'}}
