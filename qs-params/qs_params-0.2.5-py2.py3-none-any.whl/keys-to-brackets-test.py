
from qs import keysTobrackets

def test_brackets_2():
    assert keysTobrackets(['foo', 'bar']) == "foo[bar]"

def test_brackets_3():
    assert keysTobrackets(['foo', 'bar', 'foobar']) == "foo[bar][foobar]"
