import urllib
import urllib.parse
import json
import jsonuri.io

__author__ = 'guilherme'


def serialize(data, b64_encode=True, uri_encode=True):
    """Serializes a python dictionary into a Gzip, Base64 encoded string

    :param data: Python dictionary or list to serialize
    :param b64_encode: If True, the message will be compressed using Gzip and encoded using Base64
    :param uri_encode: If True, the message will be encoded with the urllib.parse.quote_plus to be used as a value of a URI parameter
    :return: Serialized data string, encoded if `encode` is `True`

    >>> from jsonuri import jsonuri
    >>> data = {"age": 31, "name": "John", "account": {"id": 127, "regions": ["US", "SG"]}}
    >>> jsonuri.serialize(data, b64_encode=True, uri_encode=False)
    'H4sIANRnb1oC/6tWSkxPVbJSMDbUUVDKS8wFsZW88jPylID8xOTk/NK8EqBQtVJmCpAyNDIHChelpmfm5xUD+dFKocEghcHuSrG1tQCN2YKETAAAAA=='
    >>> jsonuri.serialize(data, b64_encode=True, uri_encode=True)
    'H4sIAOdnb1oC%2F6tWSkxPVbJSMDbUUVDKS8wFsZW88jPylID8xOTk%2FNK8EqBQtVJmCpAyNDIHChelpmfm5xUD%2BdFKocEghcHuSrG1tQCN2YKETAAAAA%3D%3D'
=
    """

    if not isinstance(data, dict):
        raise RuntimeError("Only dictionaries are supported. The following is not a dictionary:\n %s", data)

    message = json.dumps(data)

    if b64_encode:
        message = jsonuri.io.compress(message).decode('utf-8')

    if uri_encode:
        message = urllib.parse.quote_plus(message)

    return message


def deserialize(message, b64_encoded=True, uri_encoded=True):
    """Converts an encoded message (string or bytes) into a python dictionary

    :param message: Serialized message
    :param b64_encoded: Whether the message was compressed using Gzip and encoded into Base64
    :param uri_encoded: Whether string should be decoded twice. Should be true is data was produced by this package
           and sent over the web.
    :return: Python dictionary with parsed parameters

    >>> from jsonuri import jsonuri
    >>> ser = 'H4sIAOdnb1oC%2F6tWSkxPVbJSMDbUUVDKS8wFsZW88jPylID8xOTk%2FNK8EqBQtVJmCpAyNDIHChelpmfm5xUD%2BdFKocEghcHuSrG1tQCN2YKETAAAAA%3D%3D'
    >>> jsonuri.deserialize(ser)
    >>> {'age': 31, 'name': 'John', 'account': {'id': 127, 'regions': ['US', 'SG']}}

    """

    data = message

    if uri_encoded:
        data = urllib.parse.unquote_plus(data)

    if b64_encoded:
        data = jsonuri.io.decompress(data)

    return json.loads(data)
