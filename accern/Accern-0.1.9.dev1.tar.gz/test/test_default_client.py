from accern import AccernClient, error
import pytest


def test_fails_without_token():
    with pytest.raises(error.AccernError) as exc_info:
        AccernClient.check_token(token=None)
    assert exc_info.value.args[0] == 'No token provided.'

def test_build_api_param_no_harvested_at():
    schema = {
        'filters': {
            'harvested_at': ['2017-12-26 00:00:00', '2017-12-27 00:00:00']
        }
    }
    resp = AccernClient.build_api_params(schema)
    assert 'harvested_at' not in resp and 'from' in resp
