class BaseModel:
    """Base class for all model classes.

Keyword arguments:
client -- Client instance, which will be used by model classes to fetch more data (if needed)."""
    def __init__(self, client):
        if client is None:
            raise ValueError('Client cannot bo None')
        self._client = client

    def save(self):
        raise NotImplementedError('Save not yet implemented for {}'.format(self.__class__))

    def delete(self):
        raise NotImplementedError('Delete not yet implemented for {}'.format(self.__class__))


class SampleModelClass(BaseModel):
    """Sample model class containing basic usage examples. Should be deleted."""
    def __init__(self, client, other_arg):
        super(SampleModelClass, self).__init__(client)
        self._arg = other_arg

    def run(self):
        print(self._token)
        print(self._arg)

    def delete(self):
        print('deleted')
