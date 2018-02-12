
from qserious import deserialize

result_1 = {'hola':'caracola','adios':'caracol','foo':'bar','nested':{'value': 'foobar'}}

def test_dots ():
    assert deserialize(r'hola=caracola&adios=caracol&foo=bar&nested.value=foobar') == result_1

def test_brackets ():
    assert deserialize(r'hola=caracola&adios=caracol&foo=bar&nested[value]=foobar') == result_1

def test_brackets_start ():
    assert deserialize(r'hola=caracola&adios=caracol&foo=bar&[nested]value=foobar') == result_1

def test_url ():
    assert deserialize(r'origin[url]=https%3A%2F%2Fwww.example.com%2Fitem%2Fitem_id') == {'origin':{'url':'https://www.example.com/item/item_id'}}
