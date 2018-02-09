
from qs import deserialize

result_1 = {'hola':'caracola','adios':'caracol','foo':'bar','nested':{'value': 'foobar'}}

def test_dots ():
    assert deserialize('hola=caracola&adios=caracol&foo=bar&nested.value=foobar') == result_1

def test_brackets ():
    assert deserialize('hola=caracola&adios=caracol&foo=bar&nested[value]=foobar') == result_1

def test_brackets_start ():
    assert deserialize('hola=caracola&adios=caracol&foo=bar&[nested]value=foobar') == result_1
