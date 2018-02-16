
class _DataInfo:
    def __init__(self, loader):
        self.cached = None
        self.loader = loader


class _DataItemMeta:
    def __init__(self, info, prop):
        self.info = info
        self.prop = prop


def _get_data_property(name):

    def _cached_data(self):
        info = self._data_meta[name].info  # type: _DataInfo
        if info.cached is None:
            info.cached = info.loader(self)
        return info.cached

    return property(_cached_data)


def _cycle(name, value):
    if name.startswith('_'):
        return None

    return _DataItemMeta(
        _DataInfo(value),
        _get_data_property(name),
    )


class DataMeta(type):
    """Meta class for BaseData subclasses"""
    def __new__(mcs, cls_name, bases, attrib):
        items = {}

        for base in bases:
            items.update(getattr(base, '_data_meta'))

        for name, value in attrib.items():
            item = _cycle(name, value)
            if item:
                items[name] = item

        attrib['_data_meta'] = items

        for name, item in items.items():
            attrib[name] = item.prop

        return super().__new__(mcs, cls_name, bases, attrib)
