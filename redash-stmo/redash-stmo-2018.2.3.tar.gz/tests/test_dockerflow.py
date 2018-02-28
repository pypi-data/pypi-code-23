import pytest
from flask import Flask

@pytest.fixture
def app():
    app = Flask('tests')
    return app


def test_dockerflow()
