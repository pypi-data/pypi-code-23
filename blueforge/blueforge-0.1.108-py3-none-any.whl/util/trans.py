from urllib.parse import urlparse

import requests


def download_file(save_path, file_url):
    """ Download file from http url link """

    r = requests.get(file_url)  # create HTTP response object

    with open(save_path, 'wb') as f:
        f.write(r.content)

    return save_path


def make_url(domain, location):
    """ This function helps to make full url path."""

    url = urlparse(location)

    if url.scheme == '' and url.netloc == '':
        return domain + url.path
    elif url.scheme == '':
        return 'http://' + url.netloc + url.path
    else:
        return url.geturl()


def detect_none_value(origin):
    for key in origin.keys():
        if origin[key] is None:
            del origin[key]
    return origin
