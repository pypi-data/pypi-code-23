# coding=utf-8
"""
Pass
"""

import string

import elib.console
import pytest
from elib.settings import ELIBSettings
from hypothesis import given
from hypothesis import strategies as st


@given(text=st.text())
def test_sanitize(text):
    result = elib.console._sanitize(text)
    assert isinstance(result, str)
    result.encode('ascii')


@given(text=st.text(alphabet=string.printable))
def test_info(text, capsys):
    elib.console.info(text)
    out, err = capsys.readouterr()
    assert out == 'EPAB: {}\n'.format(text)
    assert err == ''


@given(text=st.text(alphabet=string.printable))
def test_cmd_end(text, capsys):
    elib.console.cmd_end(text)
    out, err = capsys.readouterr()
    assert out == '{}\n'.format(text)
    assert err == ''


# @given(text=st.text(alphabet=string.printable))
# def test_cmd_start(text, capsys):
#     elib.console.cmd_start(text)
#     out, err = capsys.readouterr()
#     assert out == 'EPAB: {}'.format(text)
#     assert err == ''


# @given(text=st.text(alphabet=string.printable))
# def test_std_err(text, capsys):
#     elib.console.std_err(text)
#     out, err = capsys.readouterr()
#     assert out == ''
#     assert err == 'EPAB: {}\n'.format(text)


# @given(text=st.text(alphabet=string.printable))
# def test_std_out(text, capsys):
#     elib.console.std_out(text)
#     out, err = capsys.readouterr()
#     assert out == text
#     assert err == ''


# @given(text=st.text(alphabet=string.printable))
# def test_error(text, capsys):
#     elib.console.error(text)
#     out, err = capsys.readouterr()
#     assert out == ''
#     assert err == 'EPAB: {}\n'.format(text)


@pytest.mark.parametrize(
    'func,out,err',
    [
        (elib.console.info, 'EPAB: {}\n', ''),
        (elib.console.error, '', 'EPAB: {}\n'),
        (elib.console.cmd_start, 'EPAB: {}', ''),
        (elib.console.cmd_end, '{}\n', ''),
        (elib.console.std_err, '', '{}\n'),
        (elib.console.std_out, '{}', ''),
    ],
    ids=['info', 'error', 'cmd_start', 'cmd_end', 'std_err', 'std_out']
)
@given(text=st.text(alphabet=string.printable))
def test_quiet(func, out, err, text, capsys):
    ELIBSettings.quiet = False
    func(text)
    _out, _err = capsys.readouterr()
    assert _out == out.format(text)
    assert _err == err.format(text)
    ELIBSettings.quiet = True
    func(text)
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''
