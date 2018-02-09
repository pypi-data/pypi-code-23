import pytest

import jsonschema
import jsb


schema = jsb.typed(
    jsb.schema(id='/schemas/tests-jsb#', meta=jsb.draft04()),
    type='object',
    properties={
        'foo': jsb.typed(jsb.schema(), type='string'),
        'bar': jsb.typed(jsb.schema(), type='integer')
    }
)


def test_validation():
    data = {
        'foo': 'bar',
        'bar': 42
    }

    jsonschema.validate(data, schema)


def test_invalidation():
    data = {
        'foo': 'bar',
        'bar': 2.3
    }

    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(data, schema)
