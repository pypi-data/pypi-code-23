from .util import join_url, merge_dict
from .api import default as default_api


class Resource(object):
    """Base class for all REST services
    """
    convert_resources = {}

    def __init__(self, attributes=None, api=None):
        attributes = attributes or {}
        self.__dict__['api'] = api or default_api()

        super(Resource, self).__setattr__('__data__', {})
        super(Resource, self).__setattr__('error', None)
        super(Resource, self).__setattr__('headers', {})
        super(Resource, self).__setattr__('header', {})
        super(Resource, self).__setattr__('request_id', None)
        self.merge(attributes)

    def http_headers(self):
        """Generate HTTP header
        """
        return merge_dict(self.header, self.headers)

    def __str__(self):
        return self.__data__.__str__()

    def __repr__(self):
        return self.__data__.__str__()

    def __getattr__(self, name):
        return self.__data__.get(name)

    def __setattr__(self, name, value):
        try:
            # Handle attributes(error, header, request_id)
            super(Resource, self).__getattribute__(name)
            super(Resource, self).__setattr__(name, value)
        except AttributeError:
            self.__data__[name] = self.convert(name, value)

    def __contains__(self, item):
        return item in self.__data__

    def success(self):
        return self.error is None

    def merge(self, new_attributes):
        """Merge new attributes e.g. response from a post to Resource
        """
        for k, v in new_attributes.items():
            setattr(self, k, v)

    def convert(self, name, value):
        """Convert the attribute values to configured class
        """
        if isinstance(value, dict):
            cls = self.convert_resources.get(name, Resource)
            return cls(value, api=self.api)
        elif isinstance(value, list):
            new_list = []
            for obj in value:
                new_list.append(self.convert(name, obj))
            return new_list
        else:
            return value

    def __getitem__(self, key):
        return self.__data__[key]

    def __setitem__(self, key, value):
        self.__data__[key] = self.convert(key, value)

    def to_dict(self):

        def parse_object(value):
            if isinstance(value, Resource):
                return value.to_dict()
            elif isinstance(value, list):
                return list(map(parse_object, value))
            else:
                return value

        return dict((key, parse_object(value)) for (key, value) in self.__data__.items())

class Create(Resource):

    def create(self, name):
        """Creates a resource e.g. payment
        Usage::
            >>> payment = Payment({})
            >>> payment.create() # return True or False
        """
        url = join_url(self.path, name)
        new_attributes = self.api.post(url, self.to_dict())
        self.error = None
        self.merge(new_attributes)
        return self.success() and new_attributes


class Get(Resource):

    def get(self, name, fieldname='order_id'):
        url = join_url(self.path, str(self[fieldname]), name)
        return self.api.get(url)


class Post(Resource):

    def post(self, name, attributes=None, cls=Resource, fieldname='id'):
        """Constructs url with passed in headers and makes post request via
        post method in api class.

        Usage::

            >>> payment.post("execute", {'payer_id': '1234'}, payment)  # return True or False
            >>> sale.post("refund", {'payer_id': '1234'})  # return Refund object
        """
        attributes = attributes or {}
        # url = join_url(self.path, str(self[fieldname]), name)
        if not isinstance(attributes, Resource):
            attributes = Resource(attributes, api=self.api)
        new_attributes = self.api.post(url, attributes.to_dict())
        if isinstance(cls, Resource):
            cls.error = None
            cls.merge(new_attributes)
            return self.success()
        else:
            return cls(new_attributes, api=self.api)
