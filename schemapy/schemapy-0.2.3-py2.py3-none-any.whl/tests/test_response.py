from schemapy import Response, ResponseError
import pytest


class TestResponse:
    def test_invalid_constructor(self):
        with pytest.raises(ResponseError):
            Response('invalid')

    def test_repr(self):
        r = Response([])
        assert repr(r) == 'Response(count=0, fields=[])'

    def test_outofrange(self):
        r = Response([])

        with pytest.raises(IndexError):
            r[0]
