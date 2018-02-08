import pytest

from datarobot import Blueprint
from datarobot.utils import from_api


@pytest.fixture
def blueprint_data():
    return {'modelType': 'RandomForest Regressor',
            'processes': ['Missing values imputed'],
            'projectId': '5223deadbeefdeadbeef1234',
            'id': 'e1c7fc29ba2e612a72272324b8a842af'
            }


def test_instantiation(blueprint_data):
    bp = Blueprint.from_data(from_api(blueprint_data))

    assert bp.model_type == 'RandomForest Regressor'
    assert bp.processes == ['Missing values imputed']
    assert bp.project_id == '5223deadbeefdeadbeef1234'
    assert bp.id, 'e1c7fc29ba2e612a72272324b8a842af'


def test_future_proof(blueprint_data):
    Blueprint.from_data(dict(from_api(blueprint_data), new_key='future'))


def test_non_ascii(blueprint_data, unicode_string):
    bp = Blueprint.from_server_data(dict(blueprint_data, modelType=unicode_string))
    print(bp)  # test that __repr__ works correctly - this used to fail
