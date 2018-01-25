from flask import current_app

__all__ = [
    'path_to_url'
]


def path_to_url(url):
    """Convert local path to a full URL and return it"""
    if not '://' in url:
        url = '{0}://{1}{2}'.format(
            current_app.config['PREFERRED_URL_SCHEME'],
            current_app.config['SERVER_NAME'],
            url
        )
    return url