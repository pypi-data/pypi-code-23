from .api import ApiBase


class Xrea(ApiBase):
    def __init__(self, **kwargs):
        kwargs.update(base_url='https://api.xrea.com')
        super().__init__(**kwargs)


class CoreServer(ApiBase):
    def __init__(self, **kwargs):
        kwargs.update(base_url='https://api.coreserver.jp')
        super().__init__(**kwargs)
