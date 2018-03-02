from .wrappers import inside_lib
import json
from string import ascii_lowercase as lowercase

#TODO(kuba): write own exceptions

def endpoint_from(name):
    '''
    Helper function for converting class names to endpoint strings.
    For example class name "TeamMember" -> "team_member"
    '''

    return name[0].lower() + ''.join(a if a in lowercase else "_"+a.lower()
            for a in name[1:])

class BaseModel:
    """Base class for all model classes.

Keyword arguments:
id -- Number representing object in Singular
client -- Client instance, which will be used by model classes to fetch more
data (if needed)
dictionary -- Python dictionary used to fill object variables
"""
    default_client = None
    """Client: Default client used to query rest api, used if _client is None
        instance level client takes priority.
    """
    TRANSLATE_BY_ID = ()
    COMPLEX_FIELDS = ()
    def __init__(self, id=None, client=None, dictionary=None):
        """Objects may be created with or without id, if id is not present
        objecobject may be created in Singular and given id.
        Args:
            id (int): Number representing object in Singular.
            client (Client): Client instance which will be used to fetch more
                data (id needed). This client takse priority over
                default_client
            dictionary (dict): Dictionary used to fill object variables, used
            in BaseModel.all() function.

        """
        #Shoulde be isinstance(..), but cant import Client from here
        if type(client).__name__ != 'Client' and client is not None:
            raise TypeError("client schould be object of Client class")

        if client is None and self.default_client is None:
            raise ValueError('Client cannot bo None')
        self._client = client


        #Check if this object should be downloaded or created
        if id is None:
            if not issubclass(type(self), NewMixin):
                raise SyntaxError("{} object does not support "
                    "creation".format(type(self).__name__))
            self._create = True
        else:
            if not isinstance(id, int):
                raise ValueError('id must be positive int')
            if id < 0:
                raise ValueError('id must be positive')
            #This if should probably never be executed
            if not issubclass(type(self), GetSpecificMixin) \
                    or not issubclass(type(self), GetAllMixin):
                raise SyntaxError("{} object does not support "
                    "downloading".format(type(self).__name__))
            self._create = False

        #print(type(self).__name__)
        for key, value in self.COMPLEX_FIELDS.items():
            if isinstance(value, list):
                setattr(self, key, [])
        #print('after initialisation')
        self._fill_from_dict(dictionary)

        self.id = id
        self._downloaded = False
        self._saved = False
        self._deleted = False
        self.__inside_lib = False
        self.__initialised = True

    def _fill_from_dict(self, dictionary):
        """Fills object variables with data from dictionary.

        Function fills all fields from dictionary but id, id should be provided
        in __init__. COMPLEX_FIELDS class constant is used to determine whether field
        should be filled with data, or with object(or list of them) created from data

        Args:
            dictionary (dict): Data source used to fill variables
        """
        if dictionary is not None:
            for key, value in dictionary.items():
                if key == 'id' :
                    continue
                if key in self.COMPLEX_FIELDS:
                    if isinstance(self.COMPLEX_FIELDS[key], list):
                        list_ = []
                        for obj in value:
                            #Get class from COMPLEX_FIELDS
                            class_ = self.COMPLEX_FIELDS[key.lower()][0]
                            list_.append(class_(obj['id'], self._client, obj))
                        setattr(self, key, list_)
                    else:
                        if value is None:
                            setattr(self, key, None)
                        else:
                            #print(key)
                            #print(value)
                            class_ = self.COMPLEX_FIELDS[key.lower()]
                            #print(class_)
                            setattr(self, key,
                                    self.COMPLEX_FIELDS[key](value['id'],
                                    self._client, value))
                else:
                    setattr(self, key, value)

    def __setattr__(self, name, value):
        """Defined to restrict library user access and protect him from typos.
        Library users can overwrite only fields defined in FIELDS constant, id
        is not overwritable.
        """
        if not self.__dict__.get('_BaseModel__initialised', False):
            #print('in init, {} <- {}'.format(name,value))
            super.__setattr__(self, name, value)
            return
        if name == '_BaseModel__inside_lib':
            super.__setattr__(self, name, value)
            #print ('inside_lib wrapper')
            return
        if self.__dict__.get('_BaseModel__inside_lib', False):
            super.__setattr__(self, name, value)
            #print ('inside_lib func')
            return
        if name.startswith("_"):
            super.__setattr__(self, name, value)
            #print("{} <- {}".format(name,value))
            return
        if name in self.RO_FIELDS:
            raise SyntaxError("{} is READ_ONLY and should not be"
                    "changed".format(name))
        if name not in self.W_FIELDS:
            raise SyntaxError("{} is not valid object "
                    "variable".format(name))

        super.__setattr__(self, name, value)
        #print("{} <- {}".format(name, value))

    def __getattr__(self, name):
        """Defined to allow lazy acess to object variables. Objects will be
        downloaded when someone tries to acess their missing variables.
        """
        if self.__dict__.get('_BaseModel__inside_lib', False):
            #print ('inside_lib func')
            return None
        if self.__dict__.get('id', None) is None:
            raise AttributeError("{} object cannot downloads instance, "
                "'id' is missing".format(type(self).__name__))
        if name not in self.FIELDS:
            raise SyntaxError("{} is not valid {} "
                    "variable".format(name, type(self).__name__))
        if not self._downloaded and not self._create:
            if not issubclass(type(self), GetSpecificMixin):
                raise SyntaxError("{} object does not support "
                    "creation".format(type(self).__name__))
            #print("__getattr__ for {}".format(name))
            self.get()
            self._downloaded = True
        return self.__dict__.get(name)

    def save(self):
        """Used to update/create objects in Singular.
        """
        if self._create:
            self.create()
            self._create = False
        else:
            if not issubclass(type(self), UpdateMixin):
                raise SyntaxError("{} object does not support "
                    "updating".format(type(self).__name__))
            #print("updating")
            self.update()
        self._saved = True
        return True

    def _to_dict(self, exclude=[]):
        """Returns json representation of object, which can be sent to Singular

        Returns:
            str: json representing object
        """
        json_data = {}
        #print(type(self).__name__)
        for field in self.W_FIELDS:
            value = getattr(self, field)
            if value is None:
                continue
            if field in self.TRANSLATE_BY_ID:
                json_data[field] = value.id
                continue
            if field in self.COMPLEX_FIELDS:
                if isinstance(self.COMPLEX_FIELDS[field], list):
                    items= []
                    for obj in value:
                        items.append(obj._to_dict())
                    json_data[field] = items
                else:
                    json_data[field] = value._to_dict()
            elif field not in exclude:
                json_data[field] = value

        return json_data

    def __str__(self):
        return '{}(id={})'.format(type(self).__name__, self.id)

class GetAllMixin:
    """ Mixin representing option to download all objects at once.
    """
    @classmethod
    def all(cls, client=None):
        #print(cls.__name__)
        if client is None:
            #print (BaseModel.default_client)
            if BaseModel.default_client is None:
                raise TypeError("Client is missing.")
            client=BaseModel.default_client

        response, status = client._call_singular('api/'+cls.__name__.lower()+'/', 'GET')
        #TODO(kuba): check status
        #print(response, status)
        objects = []
        for obj in response:
            objects.append(cls(id=obj['id'], client=client,
                               dictionary=obj))
        return objects

class GetSpecificMixin:
    """ Mixin representing option to download specific object, specified by id
    """
    @classmethod
    def fetch(cls, id, client=None):
        #print('get classmethod')
        model_object = cls(id, client)
        model_object.get()
        return model_object

    @inside_lib
    def get(self):
        #print("Downloading {}".format(self.id))
        client = BaseModel.default_client if self._client is None else self._client
        #print("Getting: {}".format(client))
        endpoint = 'api/{}/{}/'.format(endpoint_from(self.__class__.__name__), self.id)
        response, status = client._call_singular(endpoint, 'GET')
        #print(response, status)
        if len(response) == 0:
            raise IndexError("Response is empty, make sure {} you are"
            " asking for exists".format(type(self).__name__))
        if type(response) is list:
            self._fill_from_dict(response[0])
        else:
            #print(response)
            self._fill_from_dict(response)
        #for key, value in response[0].items():
        #    super.__setattr__(self, key, value)
        self._downloaded = True


class DeleteMixin:
    """ Mixin representing option to delete specific object, specified by id
    """
    def delete_instance(self):
        client = BaseModel.default_client if self._client is None else self._client
        endpoint = 'api/{}/{}/'.format(endpoint_from(type(self).__name__), self.id)
        response, status = client._call_singular(endpoint, 'DELETE',
                json_body={'id':self.id})
        #print(response,status)
        return True

    @classmethod
    def delete(cls, id, client=None):
        endpoint = 'api/{}/{}/'.format(endpoint_from(cls.__name__), id)
        client = BaseModel.default_client if client is None else client
        response, status = client._call_singular(endpoint, 'DELETE')
        return True


class NewMixin:
    """ Mixin representing option to create objects.
    """
    @inside_lib
    def create(self):
        #print ("Creating")
        client = BaseModel.default_client if self._client is None else self._client
        endpoint = 'api/{}/'.format(endpoint_from(self.__class__.__name__))
        response, status = client._call_singular(endpoint, 'POST',
                json_body=self._to_dict())
        print(status, response)
        super.__setattr__(self, 'id', response['id'])
        self._create = False
        self._downloaded = True


class UpdateMixin:
    """ Mixin representing option to update objects.
    """
    def update(self):
        client = BaseModel.default_client if self._client is None else self._client
        endpoint = 'api/{}/{}/'.format(endpoint_from(self.__class__.__name__), self.id)
        response, status = client._call_singular(endpoint, 'PUT',
                json_body=self._to_dict())
        return status == 200
