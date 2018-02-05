from decouple import config
import pytest


@pytest.fixture
def api(request):
    from schemapy.validators import IS_OF
    from schemapy import API, DAL, Field

    dburl = getattr(
        request.module,
        'DBURL',
        config('TEST_DBURL', default='sqlite:memory')
    )

    db = DAL(dburl)
    db.define_table(
        'foo',
        Field('bar', type='string', required=True, requires=[IS_OF(str)]),
        Field('baz', type='integer', default=42, requires=[IS_OF(int)])
    )

    with API(db) as api:
        yield api


@pytest.fixture
def isof():
    from schemapy.validators import IS_OF
    return IS_OF(str)


@pytest.fixture
def isgt():
    from schemapy.validators import IS_GREATER_THAN
    return IS_GREATER_THAN(42)


@pytest.fixture
def isgte():
    from schemapy.validators import IS_GREATER_THAN_OR_EQUAL
    return IS_GREATER_THAN_OR_EQUAL(42)


@pytest.fixture
def islt():
    from schemapy.validators import IS_LESS_THAN
    return IS_LESS_THAN(42)


@pytest.fixture
def islte():
    from schemapy.validators import IS_LESS_THAN_OR_EQUAL
    return IS_LESS_THAN_OR_EQUAL(42)


@pytest.fixture
def is_in_range():
    from schemapy.validators import IS_IN_RANGE
    return IS_IN_RANGE(23, 42)


@pytest.fixture
def is_length():
    from schemapy.validators import IS_LENGTH
    return IS_LENGTH(5)