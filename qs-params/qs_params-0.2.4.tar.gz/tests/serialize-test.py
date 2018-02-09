
from qs import serialize, deserialize

data_1 = {'hola':'caracola','adios':'caracol','foo':'bar','nested':{'value': 'foobar'}}

def test_data1_1 ():
    assert serialize(data_1) == 'nested[value]=foobar&foo=bar&hola=caracola&adios=caracol'

def test_data1_2 ():
    assert deserialize(serialize(data_1)) == data_1

def test_data2 ():
    assert serialize({'nested':{'value': 'foobar'}}) == 'nested[value]=foobar'
