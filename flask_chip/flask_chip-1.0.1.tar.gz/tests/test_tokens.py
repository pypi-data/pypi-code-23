# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,redefined-outer-name,invalid-name

import time
import pytest  # type: ignore
import six

from flask_chip.tokens import generate, verify_to_value


@pytest.fixture
def key():
    return 'secretkey'


@pytest.fixture
def data():
    return {'foo': ['bar', 'baz']}


@pytest.fixture
def token(data, key):
    return generate(data, key)


@pytest.fixture
def expired_token(data, key):
    return generate(data, key, exp=0)


def test_generated_token_is_string(data, key):
    token = generate(data, key)

    assert isinstance(token, six.string_types)


def test_generated_token_contains_user_id(data, key):
    token = generate(data, key)

    result = verify_to_value(token, key)

    assert result == data


def test_return_stored_data_when_token_is_right(data, key, token):
    result = verify_to_value(token, key)

    assert result is not None
    assert result == data


def test_return_none_when_token_expire(key, expired_token):
    time.sleep(1)

    result = verify_to_value(expired_token, key)

    assert result is None


def test_return_none_when_token_is_wrong(key):
    result = verify_to_value('', key)

    assert result is None
