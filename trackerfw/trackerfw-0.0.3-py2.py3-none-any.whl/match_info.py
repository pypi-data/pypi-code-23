from contextlib import contextmanager
from aiohttp.abc import AbstractMatchInfo

class MatchInfo(AbstractMatchInfo):
    def __init__(self, route):
        super().__init__()

        self.app = None
        self._route = route
        self._current_app = None

    def add_app(self, app):
        self.app = app

    def freeze(self): pass

    def get_info(self):
        if self._route.details == None:
            return None

        return self._route.details

    @contextmanager
    def set_current_app(self, app):
        self._current_app = app
        yield
        self._current_app = None

    @property
    def expect_handler(self):
        return None

    @property
    def http_exception(self):
        return None

    @property
    def current_app(self):
        return self._current_app

    @property
    def apps(self):
        if self.app == None:
            return []

        return [self.app]

    @property
    def handler(self):
        return self._route.handler
