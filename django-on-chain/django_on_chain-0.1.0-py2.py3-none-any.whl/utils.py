from django.utils.translation import get_language

try:
    from urlparse import parse_qs, urlparse
except ImportError:  # For Python 3
    from urllib.parse import parse_qs, urlparse


def django_files_to_requests_files(files):
    return {k: (f.name, f.read(), f.content_type) for k, f in files.items()} if files is not None else None


def append_lang_param(url, param_name):
    query = urlparse(url).query
    if param_name not in parse_qs(query):
        if url[-1:][0] not in ['?', '&']:
            url += '&' if query else '?'
        url += '{}={}'.format(param_name, get_language())
    return url
