from collections import defaultdict
from threading import RLock


def pathjoin(*parts):
    all_parts = []
    traling_slash = False
    if parts and parts[-1].endswith('/'):
        traling_slash = True
    for part in parts:
        all_parts.extend(part.split('/'))
    joined = '/'.join([p for p in all_parts if p])
    if traling_slash:
        joined += '/'
    return '/%s' % joined


def yaml_config_parse(conf_fp):
    try:
        import yaml
    except ImportError:
        raise EnvironmentError(
            'To use YAML configuration please install PyYAML or '
            'install brama as `pip install brama[yaml]`'
        )
    return yaml.load(conf_fp)


def unique_items(iterable, attr_name='name'):
    '''
    Returns list without duplicated plugins/apis. Works with them as strings
    (names) and instances.
    :param iterable:
    :param attr_name: for objects in iterable, use attr's `attr_name` value
    :return: generator
    '''
    unique_set = set()
    for item in iterable:
        if isinstance(item, str):
            value = item
        else:
            value = getattr(item, attr_name)
        if value in unique_set:
            continue
        unique_set.add(value)
        yield item


class Registry(object):
    _lock = RLock()
    _items = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)
        self._items = defaultdict(dict)

    def init_app(self, app):
        self.app = app

    def add_item(self, name, value):
        if name is None:
            raise ValueError('Name is required to be registered in registry')
        if value is None:
            raise ValueError('Value of `{}` can\'t be null'.format(name))

        with self._lock:
            if name in self._items:
                raise ValueError('Already in registry: {}'.format(name))
            self._items[name] = value
        return

    def get_item(self, name):
        with self._lock:
            return self._items.get(name)

    def items(self):
        return self._items.values()
