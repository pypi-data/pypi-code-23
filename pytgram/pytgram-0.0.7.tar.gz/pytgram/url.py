"""url module.

This module contains url constants and helper function.

"""


from urllib.parse import urljoin

_BASE_URL = 'https://api.telegram.org'
_METHOD_PATH = 'bot{token}/{method}'
_FILE_PATH = 'file/bot{token}/{path}'


def get_url(url_type='method', **kwargs):
    """Makes URL.
    
    :param url_type: str. method or file.
    :param kwargs: Arguments for format method.
    :return: url.
    
    """
    path = _METHOD_PATH if url_type == 'method' else _FILE_PATH
    url = urljoin(_BASE_URL, path)
    return url.format(**kwargs) if kwargs else url
