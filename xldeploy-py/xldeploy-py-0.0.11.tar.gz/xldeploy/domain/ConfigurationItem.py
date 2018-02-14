import json

class ConfigurationItem(object):

    @staticmethod
    def as_ci(json_data):
        pjson = json.loads(json_data)
        ci = ConfigurationItem(pjson['id'], pjson['type'], pjson.copy())
        return ci

    def __init__(self, id, type, properties={}):
        self._id = id
        self._type = type
        self.__dict__['properties'] = properties

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self):
        return self._id.split('/')[-1]

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    def property(self, properties):
        self.properties = properties

    def has_property(self, key):
        return key in self.properties

    def __getattr__(self, key):
        if key in ('id', 'type', '_id', '_type', 'name'):
            object.__getattr__(self, key)
        else:
            return self.__dict__['properties'][key]

    def __setattr__(self, key, value):
        if key in ('id', 'type', '_id', '_type'):
            object.__setattr__(self, key, value)
        else:
            self.__dict__['properties'][key] = value

    def to_dict(self):
        data = {"id" : self._id, "type" : self._type}
        for key in self.properties:
            data[key] = self.properties[key]
        return data