"""Test helpers for the API"""
import requests_mock
from faker import Faker

RANDOMIZE = Faker()

def response(url: str, status_code: int = 200, method: str = 'GET', json=None) -> callable:
    """Creates a decorator that can be used to mock the given URL
    and intercept calls to it with a response of the given status code
    and JSON.

    :param str url: URL to intercept
    :param int status_code: HTTP status to respond with
    :param dict json: JSON body to respond with (optional)
    """
    def decorator(function):
        """Mock {url}, respond with HTTP {status_code}""".format(url=url, status_code=status_code)
        def mock_response(*args, **kwargs):
            print(url)
            with requests_mock.Mocker(real_http=True) as mock:
                mock.register_uri(method.upper(), url, status_code=status_code, json=json)
                return function(*args, **kwargs)
        return mock_response
    return decorator

def fake_response(response_definition, key=None):
    """Recursive method that traverses a dict response and generates
    fake data for each key, faking a successful response
    """
    from random import choice

    def is_leaf(response_definition):
        # If it ONLY  has a type key, and nothing else,
        # this is a leaf and we should generate fake data for it
        if isinstance(response_definition, dict):
            if ("type",) == tuple(response_definition.keys()):
                return True
            # If it has several keys, but no children that have a "type"
            # key of their own, this is also a leaf
            if not any(
                    filter(lambda x: "type" in x, [
                        value for key, value in response_definition.items()
                        if isinstance(value, dict)
                    ])):
                return True
            # Lists count as leaves as well
            if "type" in response_definition and response_definition["type"] == "list":
                return True
        return not response_definition

    # If the definition only contains type, we can replace this
    # object with fake data of that type
    if is_leaf(response_definition) and response_definition:
        if response_definition["type"] == 'str' and "enum" in response_definition:
            return choice(response_definition["enum"])
        elif response_definition["type"] == "list" and "items" in response_definition:
            return [fake_response(response_definition["items"])]
        elif response_definition["type"] == "dict":
            if "items" in response_definition:
                return fake_response(response_definition["items"])
            return {}
        else:
            if key and \
            (key.lower() in ("username", "email", "link", "url", "name", "responsecode") \
              or "timestamp" in key.lower()):
                return fake_data_for(key)
            else:
                return fake_data_for(response_definition["type"])

    elif isinstance(response_definition, dict):
        return {
            key: fake_response(value, key)
            for key, value in response_definition.items()
            if isinstance(value, dict) and "type" in value
        }
    else:
        return response_definition


def fake_data_for(python_type: str):
    """Generates fake data for a given type, where type can be any basic python type,
    such as int, str, float, bool; but it also supports more specific types, such as
    url, username, and email

    :param str python_type: String representation of python type
    :returns: Generated fake value
    """
    from random import randint, uniform
    python_type = python_type.lower()

    if python_type == 'int':
        return randint(0, 1000)
    elif python_type == 'bool':
        return bool(randint(0, 1))
    elif python_type == 'float':
        return uniform(0, 100)
    elif python_type == 'None':
        return None
    elif python_type == "responsecode":
        # Always return successful response since otherwise
        # we wouldnt get a response anyway
        return 200
    elif python_type == 'username':
        return RANDOMIZE.user_name()
    elif "timestamp" in python_type:
        return RANDOMIZE.unix_time()
    else:
        if hasattr(RANDOMIZE, python_type):
            return getattr(RANDOMIZE, python_type)()
        else:
            return RANDOMIZE.sentence()
  