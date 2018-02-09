import pytest
import jsb


def test_object():
    s = jsb.typed(
        jsb.schema(),
        type='object',
        properties={
            'foo': jsb.schema(id='foo')
        },
        additionalProperties=False,
        patternProperties={
            r'(bar|baz)': jsb.schema(id='barbaz')
        },
        minProperties=0,
        maxProperties=2
    )

    assert s.type == 'object'
    assert s.properties.foo.id == 'foo'
    assert s.additionalProperties is False
    assert s.patternProperties[r'(bar|baz)'].id == 'barbaz'
    assert s.minProperties == 0
    assert s.maxProperties == 2


def test_array():
    s = jsb.typed(
        jsb.schema(),
        type='array',
        items=jsb.schema(id='foo'),
        additionalItems=False,
        minItems=0,
        maxItems=42,
        uniqueItems=True
    )

    assert s.type == 'array'
    assert s['items'].id == 'foo'
    assert s.additionalItems is False
    assert s.minItems == 0
    assert s.maxItems == 42
    assert s.uniqueItems is True


def test_string():
    s = jsb.typed(
        jsb.schema(),
        type='string',
        minLength=8,
        maxLength=42,
        pattern=r'bar\.(.*)',
        format='uri'
    )

    assert s.type == 'string'
    assert s.minLength == 8
    assert s.maxLength == 42
    assert s.pattern == r'bar\.(.*)'
    assert s.format == 'uri'


@pytest.mark.parametrize('t', ['number', 'integer'])
def test_number(t):
    s = jsb.typed(
        jsb.schema(),
        type=t,
        minimum=0,
        exclusiveMinimum=True,
        maximum=42,
        exclusiveMaximum=False,
        multipleOf=2
    )

    assert s.type == t
    assert s.minimum == 0
    assert s.exclusiveMinimum is True
    assert s.maximum == 42
    assert s.exclusiveMaximum is False
    assert s.multipleOf == 2
