from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import *  # NOQA
from typing import Dict  # NOQA
from typing import List  # NOQA
from typing import Optional  # NOQA

from werkzeug.datastructures import ImmutableDict
from werkzeug.datastructures import ImmutableList


class ApiExternalDocs:
    def __init__(self):
        self.description = None  # type: str
        self.url = None  # type: str


class ApiTag:
    def __init__(self):
        self.name = None  # type: str
        self.description = None  # type: str
        self.external_docs = ApiExternalDocs()


class ApiLicense:
    def __init__(self):
        self.name = None  # type:str
        self.url = None  # type:str


class ApiContact:
    def __init__(self):
        self.email = None  # type:str


class ApiDescriptionInfo:
    def __init__(self):
        self.description = None  # type: str
        self.version = None  # type: str
        self.title = None  # type: str
        self.terms_of_service = None  # type: str
        self.contact = ApiContact()
        self.license = ApiLicense()


class ApiArrayProperty:
    def __init__(self):
        self.type = None  # type: str
        self.ref = None  # type: str


class ApiModelProperty:
    def __init__(self):
        self.name = None  # type: str
        self.type = None  # type: str
        self.format = None  # type: str
        self.items = ApiArrayProperty()


class ApiModelDefinition:
    def __init__(self):
        self.name = None  # type: str
        self.type = None  # type: str
        self._properties = {}  # type: Dict[str, ApiModelProperty]

    @property
    def properties(self):
        # type: ()->Dict[str, ApiModelProperty]
        return ImmutableDict(self._properties)

    def add_property(self, model_property):
        # type: (ApiModelProperty)->None
        self._properties[model_property.name] = model_property


class ApiKey:

    def __init__(self):
        self.type = None
        self.name = None


class SecurityDefinitions:
    def __init__(self):
        self.api_key = ApiKey()


class ApiDescription:
    def __init__(self):
        self.info = ApiDescriptionInfo()
        self.external_docs = ApiExternalDocs()
        self.security_definitions = None
        self._tags = []  # type: List[ApiTag]
        self._definitions = {}  # type: Dict[str, ApiModelDefinition]
        self._paths = {}  # type: Dict[str, ApiPathItem]

    @property
    def tags(self):
        # type: ()->List[ApiTag]
        return ImmutableList(self._tags)

    def add_tag(self, tag):
        # type: (ApiTag)->None
        self._tags.append(tag)

    @property
    def definitions(self):
        # type: ()->Dict[str, ApiModelDefinition]
        return ImmutableDict(self._definitions)

    def add_model_definition(self, model_definition):
        # type: (ApiModelDefinition)->None
        self._definitions[model_definition.name] = model_definition

    @property
    def paths(self):
        # type: ()->Dict[str, ApiPathItem]
        return ImmutableDict(self._paths)

    def set_path(self, url, path_item):
        # type: (str, ApiPathItem)->None
        self._paths[url] = path_item

    def set_security_definitions(self, security_definitions):
        # type: (SecurityDefinitions)->None
        self.security_definitions = security_definitions


class ApiResponse:
    def __init__(self):
        self.description = None  # type:str
        self.content = None


class ApiOperation:
    def __init__(self):
        self.parameters = []  # type: List[ApiParameter]
        self.description = None  # type: str
        self.summary = None  # type: str
        self.operation_id = None  # type: str
        self.request_body = None  # type: Optional[Dict[str, Any]]
        self.produces = ['application/json']
        self.tags = None  # type: Optional[List[str]]
        self._responses = {}  # type: Dict[str, ApiResponse]

    @property
    def responses(self):
        # type: ()->Dict[int, ApiResponse]
        return ImmutableDict(self._responses)

    def set_response(self, status_code, response):
        # type: (int, ApiResponse)->None
        self._responses[status_code] = response


class ApiParameter:
    def __init__(self):
        self.name = id
        self.in_ = ""
        self.description = ""
        self.required = True
        self.type = "array"
        self.items = {
            "type = string"
        }
        self.style = ""


class ApiPathItem:
    def __init__(self):
        self.summary = None  # type: str
        self.description = None  # type: str
        self.get = None  # type: ApiOperation
        self.put = None  # type: ApiOperation
        self.post = None  # type: ApiOperation
        self.delete = None  # type: ApiOperation
        self.options = None  # type: ApiOperation
        self.head = None  # type: ApiOperation
        self.patch = None  # type: ApiOperation
        self.trace = None  # type: ApiOperation
        self.servers = None  # type: ApiOperation
        self.parameters = []  # type: List[ApiParameter]
