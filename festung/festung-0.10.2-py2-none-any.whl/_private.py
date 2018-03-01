import base64
import datetime
import decimal
import urllib
import warnings

from furl import furl


# Protocol used by festing in reality. This has to be changed
# to HTTPS at some point.
PROTO = 'http'


def no_password_url(url):
    """Strip the password from the url.

    Example:

        >>> no_password_url('festung://login:password@host:8080/path')
        'festung://login:********@host:8080/path'
        >>> no_password_url('festung://login@[2001:db8::2]/path')
        'festung://login@[2001:db8::2]/path'
    """
    url = furl(url)
    if url.password is not None:
        url.password = '********'  # We don't want to leak the length of the password
    return urllib.unquote(url.url)


def to_http_url(url):
    """Convert a ``festung://`` url to the ``http`` url.

    Example:
        >>> to_http_url('festung://:password@example.com:2827/vault')
        'http://example.com:2827/vault'
        >>> to_http_url('festung://:password@[2001:db8::2]:2827/path')
        'http://[2001:db8::2]:2827/path'
        >>> to_http_url('festung://example.com:2324/vault?kdf-iter=4000')
        'http://example.com:2324/vault'
    """
    return furl(url).set(scheme=PROTO).remove(username=True, password=True, query=True).url


def to_headers(url):
    """Export HTTP headers from the `url`.

    This function extracts the 'Authorization' header and other paramters that are given in the
    query string and returns a dict of headers.

    Example::
        >>> to_headers('festung://:password@example.com:2827/vault?kdf-iter=4000') == {
        ...     'X-kdf-iter': '4000',
        ...     'Authorization': 'cGFzc3dvcmQ='}
        True
        >>> to_headers('festung://:passwd@server.tld/path?a=1') == {'Authorization': 'cGFzc3dk'}
        True
        >>> to_headers('festung://server.tld/path?b=1') == {}
        True
    """
    url = furl(url)
    headers = {}
    if url.password:
        headers['Authorization'] = base64.b64encode(url.password)
    headers.update(qs_to_headers(url.url))
    return headers


PARAM_TO_HEADER = {
    'kdf-iter': 'X-kdf-iter'
}


def qs_to_headers(url):
    return {PARAM_TO_HEADER[k]: v for k, v in furl(url).args.items() if k in PARAM_TO_HEADER}


def cast(obj):
    """Cast most python types to valid types to be serialized in JSON and passed to SQLite"""
    if isinstance(obj, bool):
        # checking bool first as it is also an instance of int
        return int(obj)
    if obj is None or isinstance(obj, (long, int, float, basestring)):
        if isinstance(obj, float):
            warnings.warn(
                "floats are highly inaccurate. Use them at your own risk.", RuntimeWarning)
        return obj

    if isinstance(obj, decimal.Decimal):
        return str(obj)

    if isinstance(obj, datetime.datetime):
        if obj.tzinfo is None:
            warnings.warn("non-timezone aware datetime can lead to many issues.", RuntimeWarning)
        return obj.isoformat()

    if isinstance(obj, (datetime.date, datetime.time)):
        return obj.isoformat()

    raise TypeError("Unserializeable type {}".format(type(obj)))
