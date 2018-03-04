import logging
from enum import Enum
from itertools import chain

from django.db.models import Model
from django.db.models.fields import DateTimeField

from .exceptions import AdharaException
from .request import APIMethods
from .response_utils import ApiResponse
from .utilities import is_reference_field

logger = logging.getLogger("adhara.response")


class ResponseModes(Enum):

    JSON = "json"
    MSG_PACK = "msg_pack"


class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    FAILURE = "failure"


class AdharaResponse:

    def __init__(self, adhara_request):
        self._request = adhara_request
        self._response_data = None
        self._status = None
        self._transformed_data = None
        self._permissions = {}
        self._error_code = 200

    def success(self, data):
        self._response_data = data
        self._status = ResponseStatus.SUCCESS

    def error(self, data, error_code=400):
        self._response_data = data
        self._status = ResponseStatus.ERROR
        self._error_code = error_code

    def failure(self, data):
        self._response_data = data
        self._status = ResponseStatus.FAILURE

    def set_permission(self, pk, name, is_permitted):
        try:
            self._permissions[pk]
        except KeyError:
            self._permissions[pk] = {}
        if is_permitted is not None:
            self._permissions[pk][name] = is_permitted

    def get_response_status(self):
        return self._status

    def _get_response_meta(self):
        return self._request.get_meta().to_dict()

    def _model_to_dict(self, instance, fields=None, exclude=None):
        opts = instance._meta
        data = {}
        fields = fields or self._request.get_meta().get_required_fields()
        for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
            skip_serialization = False
            formatted_val = None
            if type(f) == DateTimeField:
                iso_ts = f.value_from_object(instance)
                formatted_val = iso_ts.strftime('%H:%M %p, %B %d, %Y')
            elif is_reference_field(f):
                try:
                    skip_serialization = f.model._meta.get_field(f.name).rel.to.Adhara.skip_serialization
                except AttributeError:
                    pass
                if not skip_serialization:
                    value_object = getattr(instance, f.name)
                    if value_object:
                        formatted_val = {
                            "id": value_object.pk
                        }
                        try:
                            for field in value_object.Adhara.partial_fields:
                                formatted_val[field] = getattr(value_object, field)
                        except AttributeError:
                            pass
                    else:
                        formatted_val = None
            if exclude and f.name in exclude or skip_serialization:
                continue
            if fields:
                if f.name in fields:
                    data[f.name] = formatted_val if formatted_val else f.value_from_object(instance)
            else:
                data[f.name] = formatted_val if formatted_val else f.value_from_object(instance)
        sub_requests = self._request.get_sub_requests()
        # TODO get sub request model
        if sub_requests:
            from .restview import RestView
            for sub_request in sub_requests:
                sub_request.model_manager = getattr(instance, sub_request.get_model()._meta.object_name.lower()+"_set")
                transformed_data = RestView(sub_request).process().get_transformed_data()
                if sub_request.get_response_key():
                    data[sub_request.get_response_key()] = transformed_data
                elif type(transformed_data) == dict:
                    data.update(transformed_data)
                else:
                    raise AdharaException("Response key not provided")
        data = self._call_transformer(instance, data)
        return data

    def transform_row(self, data, fields=None, exclude=None):
        if isinstance(data, Model):
            dict_response = self._model_to_dict(data, fields=fields, exclude=exclude)
            if self._permissions:
                try:
                    if self._permissions[data.pk]:
                        dict_response["_permissions"] = self._permissions[data.pk]
                except KeyError:
                    pass
            return dict_response
        else:
            return data

    def get_request(self):
        return self._request

    def get_data(self):
        return self._response_data

    def _call_transformer(self, row, transformed_row):
        if self._request.transformer:
            transformed = self._request.transformer(row, transformed_row)
            return transformed if transformed is not None else transformed_row

    def _call_list_transformer(self, entries, transformed_data):
        if self._request.list_transformer:
            transformed = self._request.list_transformer(entries, transformed_data)
            return transformed if transformed is not None else transformed_data

    def transform_data(self):
        if self.get_response_status() == ResponseStatus.SUCCESS:
            # TODO integrate with model to dict
            if type(self.get_data()) == list:
                transformed_data = []
                data = self.get_data()
                for row in data:
                    transformed_data.append(self.transform_row(row))
                transformed_data = self._call_list_transformer(data, transformed_data)
            else:
                transformed_data = self.transform_row(self.get_data())
            self._transformed_data = transformed_data
        else:
            self._transformed_data = self.get_data()

    def get_transformed_data(self):
        if not self._transformed_data:
            self.transform_data()
        return self._transformed_data

    def get_response(self):
        response = {
            "data": self.get_transformed_data(),
            "status": self._status.value
        }
        if self._request.get_method() == APIMethods.GET_LIST:
            meta = self._get_response_meta()
            if meta:
                response["meta"] = meta
        return response

    def serialize(self, dict_response=None, response_mode=ResponseModes.JSON):
        dict_response = dict_response or self.get_response()
        if response_mode == ResponseModes.JSON:
            if self._status == ResponseStatus.FAILURE:
                return ApiResponse.AsiddhauPratikriyaa(dict_response)
            elif self._status == ResponseStatus.ERROR:
                if self._error_code == 403:
                    return ApiResponse.NotAllowedPratikriyaa(dict_response)
                return ApiResponse.SkhalitaPratikriyaa(dict_response)
            else:
                return ApiResponse.Pratikriyaa(dict_response)
