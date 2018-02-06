import six
import trafaret as t

from datarobot.client import get_client, staticproperty
from datarobot.utils import from_api


class APIObject(object):
    _client = staticproperty(get_client)
    _converter = t.Dict({}).allow_extra('*')

    @classmethod
    def _fields(cls):
        return {k.to_name or k.name for k in cls._converter.keys}

    @classmethod
    def from_data(cls, data):
        checked = cls._converter.check(data)
        safe_data = cls._filter_data(checked)
        return cls(**safe_data)

    @classmethod
    def from_location(cls, path):
        server_data = cls._server_data(path)
        return cls.from_server_data(server_data)

    @classmethod
    def from_server_data(cls, data):
        """
        Instantiate an object of this class using the data directly from the server,
        meaning that the keys may have the wrong camel casing

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        """
        case_converted = from_api(data)
        return cls.from_data(case_converted)

    @classmethod
    def _filter_data(cls, data):
        fields = cls._fields()
        return {key: value
                for key, value in six.iteritems(data)
                if key in fields}

    @classmethod
    def _safe_data(cls, data):
        return cls._filter_data(cls._converter.check(from_api(data, do_recursive=False)))

    @classmethod
    def _server_data(cls, path):
        return cls._client.get(path).json()
