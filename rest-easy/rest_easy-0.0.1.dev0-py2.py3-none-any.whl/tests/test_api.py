# -*- coding: utf-8 -*-
"""Test the API."""

from flask import Flask


from rest_easy.api import API


def flask_app():
    return Flask(__name__)


class TestSetup:
    """Test the setup & population of the API class."""

    def test_application_attr(self):
        """Validate the flask app is stored on the instance."""
        app = flask_app()
        assert API(app).application is app
