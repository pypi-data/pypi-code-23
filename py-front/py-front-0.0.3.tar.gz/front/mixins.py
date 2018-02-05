from front.api import client


class Readable(object):
    def read(self):
        path = self._get_path()
        data = self._load_raw(client.get(path))
        self._orig_data = data
        self._set_fields(data)

    def _get_path(self):
        if getattr(self, 'id', None) is None:
            raise ValueError('%s must be saved before it is read' % self)
        return self.Meta.detail_path.format(id=self.id)


class Creatable(object):
    def create(self):
        if hasattr(self, 'id'):
            raise ValueError(
                '%s cannot be created; it already has an id' % self
            )
        data = client.post(self.Meta.create_path, json=self._raw_data)
        self._set_fields(self._load_raw(data))
