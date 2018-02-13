import os
from abc import ABCMeta, abstractmethod

import pytest
from simple_settings import settings
from webtest import TestApp


class APITestCase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def app_cls(self):
        raise NotImplementedError

    @abstractmethod
    def setup_mounts(self, app):
        pass

    @abstractmethod
    def settings_module(self) -> str:
        raise NotImplementedError

    @pytest.yield_fixture()
    def app(self):
        os.environ['settings'] = self.settings_module()
        settings._dict = {}  # Reset settings for every test
        app = self.app_cls()()
        self.setup_mounts(app)

        app.setup()

        yield app

    @pytest.yield_fixture()
    def wsgi(self, app):
        yield TestApp(app.wsgi_application)
