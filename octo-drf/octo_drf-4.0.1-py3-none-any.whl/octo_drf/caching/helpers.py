


from django.conf import settings


def with_caching_options(default_cls, caching_cls, layer=''):
    """
    Принимает дефолтный класс для вью или модели, возвращает класс с методами для кеша,
    если кеш включен в настройках
    """
    from importlib import import_module
    if settings.CACHING:
        cache_module = import_module('octo_drf.caching.{}'.format(layer))
        return getattr(cache_module, caching_cls)
    return default_cls


def set_max_age(seconds=None, minutes=None, hours=None, days=None):
    if seconds:
        return seconds
    elif minutes:
        return 60 * minutes
    elif hours:
        return 60 * 60 * hours
    else:
        return 60 * 60 * 24 * days


def set_cache_headers(last_modified, max_age):
    headers = {}
    if last_modified:
        headers['Last-Modified'] = last_modified
    elif max_age:
        headers['Cache-Control'] = 'max-age={}'.format(max_age)
    return headers
