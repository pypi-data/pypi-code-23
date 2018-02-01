
class _DataInfo:
    def __init__(self, loader):
        self.cached = None
        self.loader = loader


def _get_data_property(hidden_name):

    def _cached_data(self):
        info = getattr(self, hidden_name)  # type: _DataInfo
        if info.cached is None:
            info.cached = info.loader(self._workspace)
        return info.cached

    return property(_cached_data)


class DataMeta(type):
    """Meta class for BaseData subclasses"""
    def __new__(mcs, cls_name, bases, attrib):
        mapping = {}

        for name, value in attrib.items():
            if name.startswith('_'):
                mapping[name] = value
                continue

            hidden_name = '_' + name

            mapping[hidden_name] = _DataInfo(value)
            mapping[name] = _get_data_property(hidden_name)

        return super().__new__(mcs, cls_name, bases, mapping)
