# -*- coding: utf-8 -*-

import pytest

from flask import Flask


def cfg():
    return {
        'TESTING': True,
        'SECRET_KEY': 'secret',
    }


def create_app(config):
    app = Flask(__name__)

    # config
    for key, value in config.items():
        app.config[key] = value

    return app


@pytest.fixture
def app(request):
    app = create_app(cfg())

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture
def config(app):
    return app.config


@pytest.fixture
def client(app):
    return app.test_client()
