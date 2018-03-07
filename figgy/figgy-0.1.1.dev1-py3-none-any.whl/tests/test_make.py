"""Test the make module."""

import figgy
import os
import pytest
import json

path = 'tests/'
filename = 'config'
format = 'json'
outpath = '{p}{fn}.{fmt}'.format(p=path, fn=filename, fmt=format)
data = {'spam': 'sausage', 'ham': 'sausage'}
data2 = {'spam': 'eggs', 'ham': 'baked beans'}


def setup_function(function):
    """Set up a new state."""
    pass


def teardown_function(function):
    """Tear down state set up with a setup_function call or in function."""
    files = [outpath, 'tests/spam.json']
    for f in files:
        try:
            os.remove(f)
        except OSError:
            pass


def test_args_none():
    """Should return TypeError."""
    with pytest.raises(TypeError):
        figgy.make()


def test_arg_data_none_error():
    """Should return an error if the input data is bad."""
    bad_input_datas = [
        None, False, True,
        1, 0, 0.1, complex('j'),
        [], [0, 1], (), (0, 1),
        range(0), range(1),
        '', 'spam',
        b'', b'spam',
        bytearray(), bytearray(b'\xf0\xf1'),
        {}, {0, 1}
    ]
    with pytest.raises(TypeError):
        for bad_input_data in bad_input_datas:
            figgy.make(data=None)


def test_get_gets_dict(monkeypatch):
    """Should get a dict when we supply the get argument."""
    monkeypatch.setattr('builtins.input', lambda x: "I'll do you for that.")
    assert isinstance(figgy.make(data=data, path=path, get=True), dict)


def test_arg_filename_blank_returns_config(monkeypatch):
    """Should get something called 'config' if there's no argument."""
    monkeypatch.setattr('builtins.input', lambda x: "Spam, spam, spam, spam.")
    assert 'config' in list(
        figgy.make(data=data, path=path, get=True).keys())[0]


def test_arg_filename_supplied_returns_arg_in_returned_dict(monkeypatch):
    """Should get dict with first key returning the input filename."""
    monkeypatch.setattr(
        'builtins.input', lambda x: "cabbage crates coming over the briny?")
    assert 'spam' in list(figgy.make(
        data=data, get=True, filename='spam', path=path
    ).keys())[0].split('.')[0]


def test_args_filename_and_path_concat_in_returned_dict(monkeypatch):
    """Should combine the args for the file write destination."""
    monkeypatch.setattr('builtins.input', lambda x: "What-ho, Squiffy.")
    assert outpath.split('.')[0] == list(
        figgy.make(
            data=data, get=True, filename=filename, path=path
        ).keys())[0].split('.')[0]


def test_file_creation(monkeypatch):
    """A file should have been created."""
    monkeypatch.setattr('builtins.input', lambda x: "Jolly good. Fire away.")
    figgy.make(data=data, path=path)
    assert os.path.exists(outpath)


def test_file_is_valid_format_json(monkeypatch):
    """We should get a valid json file created."""
    monkeypatch.setattr(
        'builtins.input', lambda x: "sausage squad up the blue end?")
    figgy.make(data=data, path=path)
    assert json.load(open(outpath))


def test_if_file_exists_returns_error(monkeypatch):
    """If there is already a file we should not rewrite it."""
    monkeypatch.setattr(
        'builtins.input', lambda x: "Bunch of monkeys on the ceiling")
    figgy.make(data=data, path=path)
    with pytest.raises(Exception):
        figgy.make(data=data2, path=path)


def test_arg_force_true_results_in_file(monkeypatch):
    """If force is true we should make a file even if there was a file."""
    monkeypatch.setattr(
        'builtins.input', lambda x: "let's get the bacon delivered!")
    figgy.make(data=data, path=path)
    figgy.make(data=data2, path=path, force=True)
    assert os.path.exists(outpath)


def test_arg_force_true_creates_file_with_second_input_data(monkeypatch):
    """The file we made should have the data from the second call."""
    monkeypatch.setattr('builtins.input', lambda x: "sausage")
    figgy.make(data=data2, path=path)
    figgy.make(data=data, path=path, force=True)
    assert json.load(open(outpath)) == data


def test_input_matches_output(monkeypatch):
    """Do the file keys and values match the input."""
    monkeypatch.setattr('builtins.input', lambda x: "sausage")
    config = figgy.make(data=data, path=path, get=True)
    assert data == config[outpath]


def test_tilde_path_raises_filenotfounderror(monkeypatch):
    """Using a path with a tilde should result in a specific error."""
    monkeypatch.setattr('builtins.input', lambda x: "Ex-parrot")
    with pytest.raises(Exception):
        figgy.make(data=data, path='~/')


# Tests for features planned for future releases
# unmark this and write a more complete test
@pytest.mark.xfail
def test_arg_format():
    """The promptcontext argument is not supported yet."""
    assert figgy.make(data=data, path=path, promptcontext=True)


# unmark this and write a more complete test
@pytest.mark.xfail
def test_arg_promptcontext():
    """The promptcontext argument is not supported yet."""
    assert figgy.make(data=data, path=path, promptcontext=True)


# unmark this and write a more complete test
@pytest.mark.xfail
def test_path_expansion(monkeypatch):
    """A 'NIX tilde should expand to the user path."""
    monkeypatch.setattr('builtins.input', lambda x: "bacon")
    tilde_path = '~/{p}'.format(p=path)
    assert outpath.split('.')[0] == list(
        figgy.make(
            data=data, get=True, filename=filename, path=tilde_path
        ).keys())[0].split('.')[0]


# Test pytest itself
def test_teardown_tears_down():
    """If teardown works we should not have a file at this path."""
    assert not os.path.exists(outpath)
