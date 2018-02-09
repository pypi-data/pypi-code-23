import jsb


def test_typed():
    s = jsb.typed(jsb.schema(), type='test')
    assert s.type == 'test'


def test_require():
    s = jsb.require(jsb.schema(), 'foo', 'bar')
    assert s.required == ['foo', 'bar']


def test_oneOf():
    s1 = jsb.schema(id='s1')
    s2 = jsb.schema(id='s2')
    s3 = jsb.schema(id='s3')

    s = jsb.oneOf(s1, s2, s3)
    assert len(s.oneOf) == 2
    assert s.oneOf[0].id == 's2'
    assert s.oneOf[1].id == 's3'

    s = jsb.oneOf(s1)
    assert 'oneOf' not in s


def test_anyOf():
    s1 = jsb.schema(id='s1')
    s2 = jsb.schema(id='s2')
    s3 = jsb.schema(id='s3')

    s = jsb.anyOf(s1, s2, s3)
    assert len(s.anyOf) == 2
    assert s.anyOf[0].id == 's2'
    assert s.anyOf[1].id == 's3'

    s = jsb.anyOf(s1)
    assert 'anyOf' not in s


def test_allOf():
    s1 = jsb.schema(id='s1')
    s2 = jsb.schema(id='s2')
    s3 = jsb.schema(id='s3')

    s = jsb.allOf(s1, s2, s3)
    assert len(s.allOf) == 2
    assert s.allOf[0].id == 's2'
    assert s.allOf[1].id == 's3'

    s = jsb.allOf(s1)
    assert 'allOf' not in s


def test_not():
    s1 = jsb.schema(id='s1')
    s2 = jsb.schema(id='s2')

    s = jsb.not_(s1, s2)
    assert s['not'].id == 's2'


def test_enum():
    s = jsb.enum(jsb.schema(), 'hello', 'world')
    assert s.enum == ['hello', 'world']

    s = jsb.enum(jsb.schema())
    assert 'enum' not in s


def test_default():
    s = jsb.default(jsb.schema(), 'foo')
    assert s.default == 'foo'


def test_deps():
    s = jsb.dependencies(
        jsb.schema(),
        foo=jsb.schema(id='foo'),
        bar=['baz']
    )
    assert s.dependencies.foo.id == 'foo'
    assert s.dependencies.bar == ['baz']
