import pytest

from pymongal.database_dict import DictDatabase


@pytest.fixture(autouse=True)
def db():
    return DictDatabase({
        'project': [
            project1.copy(), project2.copy()
        ]
    })


from tests.common_tests import *
