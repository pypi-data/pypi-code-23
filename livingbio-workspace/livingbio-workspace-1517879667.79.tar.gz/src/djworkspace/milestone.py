from functools import wraps
from itertools import izip

from .cache import lrucache
from .models import Cache

checkpoint = lrucache


def checklist(key_str):
    def _lru_cache(func):
        @wraps(func)
        def wrapper(alist, *args, **kwargs):
            keys = [key_str.format(k, *args, **kwargs) for k in alist]
            type = '{}.{}'.format(func.__module__, func.__name__)

            item_key = dict(izip(alist, keys))
            key_value = {}

            for key in keys:
                try:
                    key_value[key] = Cache.objects.get(
                        key=key, type=type).results
                except Cache.DoesNotExist:
                    pass

            items_not_checked = [
                k for k in item_key if item_key[k] not in key_value]

            if items_not_checked:
                results = func(items_not_checked, *args, **kwargs)

                for item, result in izip(items_not_checked, results):
                    key = item_key[item]
                    Cache.objects.update_or_create(
                        key=key,
                        type=type,
                        defaults={
                            "results": result
                        }
                    )
                    key_value[item_key[item]] = result

            return [key_value[item_key[item]] for item in alist]

        return wrapper

    return _lru_cache


def uncheck(type=None, key=None):
    queryset = Cache.objects
    if type:
        queryset = queryset.filter(type=type)
    if key:
        queryset = queryset.filter(key=key)

    return queryset.delete()
