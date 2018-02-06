import pytest
from ..cache import lrucache
from ..models import Cache


@lrucache('{0}+{1}')
def sum(a, b):
    return a + b


@lrucache("{0}")
def show(msg):
    return msg


@pytest.mark.django_db
def test_cache():
    a = 1
    b = 2
    c = sum(a, b)

    assert c == 3

    try:
        Cache.objects.get(key="1+2")
    except Exception:
        pytest.fail("Cache not created")


@pytest.mark.django_db
def test_cache_with_long_key():
    result = show("x" * 200)
    assert result == "x" * 200

    result_cache = show("x" * 200)
    assert result_cache == result
