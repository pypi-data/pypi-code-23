"""Test the specification classes."""


from rest_easy.specification import fields
from rest_easy.specification import Specification
from rest_easy.specification.core import SpecificationMeta


def test_specification_works_like_marshmallow():
    """Verify we haven't *lost* functionality."""

    class Schema(Specification):
        foo = fields.String()
        bar = fields.Integer()

    data = {'foo': 'foo', 'bar': '13'}
    exp = {'foo': 'foo', 'bar': 13}

    loaded = Schema().load(data).data
    dumped = Schema().dump(data).data

    assert loaded == dumped == exp
