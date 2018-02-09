
from qs import bracketsToDots

def test_brackets_1():
    assert bracketsToDots("[foo]bar") == "foo.bar"
    assert bracketsToDots("[foo][bar]") == "foo.bar"
    assert bracketsToDots("foo[bar]") == "foo.bar"

def test_brackets_2():
    assert bracketsToDots("foo[bar][foobar]") == "foo.bar.foobar"
    assert bracketsToDots("[foo][bar]foobar") == "foo.bar.foobar"
