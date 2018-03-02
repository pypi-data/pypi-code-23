""" Utility functions.
"""


def get_ip(request):
    environ = getattr(request, 'environ', {})

    if "HTTP_X_FORWARDED_FOR" in environ:
        return environ.get('HTTP_X_FORWARDED_FOR')

    if 'REMOTE_ADDR' in environ:
        return environ.get('REMOTE_ADDR')

    return environ.get('HTTP_HOST', None)


def get_user_data(request):
    try:
        user = request.get('AUTHENTICATED_USER')
    except AttributeError:
        return dict(user='NO_REQUEST', ip='NO_REQUEST')

    username = getattr(user, 'getUserName', lambda: 'unknown')()
    req = getattr(user, 'REQUEST', request)
    return dict(user=username, ip=get_ip(req))
