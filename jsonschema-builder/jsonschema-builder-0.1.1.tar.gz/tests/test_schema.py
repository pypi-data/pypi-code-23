import jsb


def test_schema():
    got = jsb.schema(
        id='test',
        title='test',
        description='test',
        meta=jsb.draft04()
    )
    assert got.id == 'test'
    assert got.title == 'test'
    assert got.description == 'test'
    assert got['$schema'] == jsb.draft04()


def test_define():
    s1 = jsb.schema(id='s1')
    s2 = jsb.schema(id='s2')
    s3 = jsb.define(s1, 's2', s2)

    assert s3.id == s1.id
    assert s2.id in s3.definitions
    assert s3.definitions.s2.id == s2.id


def test_ref():
    r = jsb.ref('test')
    assert r['$ref'] == '#/definitions/test'
