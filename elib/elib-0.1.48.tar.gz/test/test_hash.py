# coding=utf-8
from pathlib import Path

import pytest

import elib


def test_get_hash_from_string():
    test_string = 'this is some dummy test string'
    assert elib.hash_.get_hash(test_string) == 'f4c8f848b02d640c75a2385fd315412b'
    assert elib.hash_.get_hash(
        test_string,
        'sha256'
    ) == '556d2c0500f5e1e40925e65d16cc3c46006006e88ffc5051fb3a7f7c1b6af9b1'


def test_get_hash_from_file():
    test_file = Path('./test_file')
    test_file.write_text('this is some dummy test string')
    assert elib.hash_.get_hash(test_file.read_bytes()) == 'f4c8f848b02d640c75a2385fd315412b'
    assert elib.hash_.get_hash(
        test_file.read_bytes(),
        'sha256'
    ) == '556d2c0500f5e1e40925e65d16cc3c46006006e88ffc5051fb3a7f7c1b6af9b1'


def test_get_hash_wrong_method():
    with pytest.raises(RuntimeError):
        elib.hash_.get_hash('test', 'nope')
