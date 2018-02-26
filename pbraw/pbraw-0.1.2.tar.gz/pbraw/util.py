try:
    from urllib.parse import urlparse as _urlparse
    from urllib.parse import urlunparse as _urlunparse
except ImportError: #py2
    from urlparse import urlparse as _urlparse
    from urlparse import urlunparse as _urlunparse

urlparse = _urlparse
urlunparse = _urlunparse

import requests

from requests.exceptions import ConnectionError, Timeout

class _get_url():
    """Memoizing requests::get"""
    def __init__(self):
        self._results = {}

    def __call__(self, uri):
        if uri in self._results:
            return self._results[uri]
        try:
            res = requests.get(uri)
            res.raise_for_status()
        except (ConnectionError, Timeout): # user might have net problems, reraise?
            # do not memoize
            return None
        except:
            self._results[uri] = None
            return None
        self._results[uri] = res
        return res

get_url = _get_url()
