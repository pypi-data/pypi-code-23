# -*- coding: utf-8 -*-

from pipesnake.base import Transformer


class FakeTransformer(Transformer):
    def __init__(self, name):
        super(FakeTransformer, self).__init__(name=name)

    def fit(self, x, y):
        pass

    def transform(self, x, y):
        pass

    def inverse_transform(self, x, y):
        pass

    def get_params(self):
        pass

    def set_params(self, a, b):
        pass
