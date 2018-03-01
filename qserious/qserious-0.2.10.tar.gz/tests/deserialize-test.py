
from qserious import deserialize

result_1 = {
    'hola': 'caracola',
    'adios': 'caracol',
    'foo': 'bar',
    'nested': {'value': 'foobar'}
}
result_2 = {
    'origin': {
        'url': 'https://www.example.com/item/item_id'
    }
}


def test_dots():
    qs = r'hola=caracola&adios=caracol&foo=bar&nested.value=foobar'
    assert deserialize(qs) == result_1


def test_brackets():
    qs = r'hola=caracola&adios=caracol&foo=bar&nested[value]=foobar'
    assert deserialize(qs) == result_1


def test_brackets_start():
    qs = r'hola=caracola&adios=caracol&foo=bar&[nested]value=foobar'
    assert deserialize(qs) == result_1


def test_url():
    qs = r'origin[url]=https%3A%2F%2Fwww.example.com%2Fitem%2Fitem_id'
    result = deserialize(qs)
    assert result == {
        'origin': {'url': 'https://www.example.com/item/item_id'}
    }
