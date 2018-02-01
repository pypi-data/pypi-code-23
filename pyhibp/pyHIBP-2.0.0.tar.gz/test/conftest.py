import time

import pytest

import pyHIBP


@pytest.fixture(autouse=True)
def rate_limit():
    # The HIBP API has a ratelimit of 1500ms. Sleep for 2 seconds.
    time.sleep(2)


@pytest.fixture(autouse=True)
def dev_user_agent(monkeypatch):
    monkeypatch.setattr(pyHIBP, 'pyHIBP_USERAGENT', "pyHIBP: A Python Interface to the Public HIBP API <testing suite>")
