import trafaret as t

from datarobot.models.api_object import APIObject


class Dummy(APIObject):

    _converter = t.Dict({
        t.Key('renamed') >> 'magic': t.String()
    })

    def __init__(self, magic=None):
        self.magic = magic


def test_safe_data():
    data = Dummy._safe_data({'renamed': 'nombre'})
    dummy = Dummy(**data)
    assert dummy.magic == 'nombre'
