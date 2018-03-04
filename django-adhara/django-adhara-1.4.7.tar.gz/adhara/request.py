from .session import Session
from .meta import Meta
from enum import Enum


class APIMethods(Enum):
    GET = "GET"
    GET_LIST = "GET_LIST"
    GET_COUNT = "GET_COUNT"
    GET_EXISTS = "GET_EXISTS"
    POST = "POST"
    PUT = "PUT"
    BULK_PUT = "BULK_PUT"
    DELETE = "DELETE"
    BULK_DELETE = "DELETE"


class Criteria:

    def __init__(self, criteria=None, identifier=None):
        self._criteria = criteria or {}
        self._identifier = identifier

    def update_identifier(self, identifier):
        self._identifier = identifier

    def set_criteria(self, criteria=None):
        self._criteria = criteria or {}

    def get_criteria(self):
        if self._identifier:
            criteria = {"pk": self._identifier}
            criteria.update(self._criteria)
        else:
            criteria = self._criteria
        return criteria

    def update_criteria(self, criteria):
        self._criteria.update(criteria)


class AdharaRequest:

    def __init__(self, request, *, model=None, method=None, input_json=None, identifier=None,
                 meta=None, criteria=None, exclude_criteria=None, response_key=None, transformer=None,
                 list_transformer=None):
        self._request = request
        self._model = model
        self._identifier = identifier
        self._input_json = input_json
        self._identifier = identifier
        self._method = None
        self._set_method_(method)
        self._meta = meta or Meta()
        self._criteria = Criteria(criteria, identifier)
        self._exclude_criteria = Criteria(exclude_criteria)
        self._sub_requests = []
        self._response_key = response_key
        self.transformer = transformer
        self.list_transformer = list_transformer
        self.is_sub_request = False
        self.model_manager = None

    def _get_method_for(self, method, identifier):
        if method in [APIMethods.GET, APIMethods.GET_LIST]:
            return APIMethods.GET if identifier else APIMethods.GET_LIST
        if method in [APIMethods.DELETE, APIMethods.BULK_DELETE]:
            return APIMethods.DELETE if identifier else APIMethods.BULK_DELETE
        if method in [APIMethods.PUT, APIMethods.BULK_PUT]:
            return APIMethods.PUT if identifier else APIMethods.BULK_PUT
        return method

    def _set_method_(self, method=None):
        self.set_method(self._get_method_for(method or self.get_method(), self.get_identifier()))

    def get_method(self):
        return self._method

    def set_method(self, method):
        self._method = method

    def get_criteria_object(self):
        return self._criteria

    def set_exclude_criteria(self, exclude_criteria):
        if isinstance(exclude_criteria, Criteria):
            self._exclude_criteria = exclude_criteria
        else:
            self._exclude_criteria = Criteria(exclude_criteria, self.get_identifier())

    def get_exclude_criteria_object(self):
        return self._exclude_criteria

    def get_meta(self):
        return self._meta

    def get_input(self):
        required_input = {
            "request": self._request
        }
        if self._input_json:
            required_input.update(self._input_json)
        if 'id' in required_input:
            del required_input['id']
        return required_input

    def update_input(self, update_data):
        if not self._input_json:
            self._input_json = {}
        self._input_json.update(update_data)

    def get_identifier(self):
        return self._identifier

    def set_identifier(self, identifier=None):
        self._identifier = identifier
        if self.get_criteria_object():
            self.get_criteria_object().update_identifier(identifier)
        if self.get_exclude_criteria_object():
            self.get_exclude_criteria_object().update_identifier(identifier)
        self._set_method_()

    def set_new_identifier(self, new_identifier):
        self._identifier = new_identifier

    def get_tenant_db(self):
        return Session.get_db(self._request)

    def get_http_request(self):
        return self._request

    def add_sub_request(self, sub_request):
        sub_request.is_sub_request = True
        self._sub_requests.append(sub_request)

    def get_sub_requests(self):
        return self._sub_requests

    def set_model(self, model):
        self._model = model

    def get_model(self):
        return self._model

    def get_model_manager(self):
        if self.is_sub_request:
            return self.model_manager
        return self.get_model().objects

    def get_response_key(self):
        return self._response_key
