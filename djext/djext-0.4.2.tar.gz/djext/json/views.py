from jsonschema import Draft4Validator, Draft3Validator
from jsonschema.validators import validator_for

from .http.response import JsonResponseBadRequest


class JsonFormMixin(object):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT', 'PATCH') and not self.request.POST \
                and hasattr(self.request, 'json') and self.request.json:
            kwargs['data'] = self.request.json
        return kwargs

    def form_invalid(self, form):
        errors = {
            field: [error for data in error_list.data for error in data]
            for field, error_list in form.errors.items()
        }
        return JsonResponseBadRequest({'errors': errors})


class JsonSchemaPayloadMixin(object):
    request_schema = {}

    def dispatch(self, request, *args, **kwargs):
        """
        :param django.core.handlers.wsgi.WSGIRequest request:
        :param args:
        :param kwargs:
        :return:
        """
        if request.method in ('POST', 'PUT', 'PATCH'):
            if self.request_schema:
                validator_cls = validator_for(self.request_schema)
                validator = validator_cls(self.request_schema)  # type: Draft4Validator or Draft3Validator
                errors = validator.iter_errors(request.json)
                if errors:
                    return JsonResponseBadRequest({'errors': errors})
        return super().dispatch(request, *args, **kwargs)

