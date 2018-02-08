import pytest

from datarobot import Client
from datarobot.client import get_client


def test_missing_token_in_env_fails(clean_env):
    clean_env.setenv('DATAROBOT_ENDPOINT', 'https://home.com')
    with pytest.raises(ValueError):
        get_client()


def test_missing_endpoint_in_config_fails():
    with pytest.raises(ValueError):
        Client(token='a-token')


def test_missing_token_in_config_fails():
    with pytest.raises(ValueError):
        Client(endpoint='https://host_name.com')


@pytest.mark.usefixtures('no_version_check')
def test_file_config_with_connect_timeout(clean_user_config, default_config_token,
                                          default_config_endpoint):
    fcontent = 'endpoint: {}\ntoken: {}\nconnect_timeout: 23'.format(
        default_config_endpoint,
        default_config_token
    )
    clean_user_config.write(fcontent)
    client = get_client()
    assert client.connect_timeout == 23


def test_code_config_with_connect_timeout(code_config_token, code_config_endpoint):
    Client(token=code_config_token, endpoint=code_config_endpoint,
           connect_timeout=24)
    c = get_client()
    assert c.connect_timeout == 24
