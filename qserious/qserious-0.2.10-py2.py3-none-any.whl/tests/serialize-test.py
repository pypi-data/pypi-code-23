
from qserious import serialize, deserialize

data_1 = {
    'hola': 'caracola',
    'adios': 'caracol',
    'foo': 'bar',
    'nested': {
        'value': 'foobar'
    }
}


def test_data1_1():
    espected = 'nested[value]=foobar&foo=bar&hola=caracola&adios=caracol'
    assert serialize(data_1) == espected


def test_data1_2():
    assert deserialize(serialize(data_1)) == data_1


def test_data2():
    data = {'nested': {'value': 'foobar'}}
    expected = 'nested[value]=foobar'
    assert serialize(data) == expected
