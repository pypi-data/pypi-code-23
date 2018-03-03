import pytest

from jinjafy import _parse_template_var_string


def test_valid_template_string():
    assert _parse_template_var_string('foo=bar') == ('foo', 'bar')

def test_invalid_template_string():
    with pytest.raises(ValueError):
        assert _parse_template_var_string('foobar')

    with pytest.raises(ValueError):
        assert _parse_template_var_string('foo = bar = baz')

def test_handles_spaces():
    assert _parse_template_var_string('ohana = means family'), ('ohana', 'means family')
