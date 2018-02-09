from schemapy.exceptions import ActionError
from schemapy.response import Response

from pydal.objects import Table
from addict import Dict


class Action:
    def __init__(
        self,
        api,
        name,
        type='read',
        request=None,
        response=None,
        fn=None,
        ismethod=False,
        **kwargs
    ):
        if type not in ['create', 'read', 'update', 'delete']:
            raise ActionError('type must be create, read, update or delete')

        if not callable(fn):
            raise ActionError('fn must be callable')

        if request is None:
            request = []

        if response is None:
            response = []

        if isinstance(request, Table):
            request = [
                getattr(request, field)
                for field in request.fields
            ]

        if isinstance(response, Table):
            response = [
                getattr(response, field)
                for field in response.fields
            ]

        self.api = api
        self.name = name
        self.type = type
        self.request = request
        self.response = response
        self.fn = fn
        self.ismethod = ismethod

        for attrname, attrval in kwargs.items():
            setattr(self, attrname, attrval)

    def __call__(self, *args, **kwargs):
        req = Dict()

        for field in self.request:
            if field.required and field.name not in kwargs:
                raise ActionError(
                    'Missing required field: {0}'.format(field.name)
                )

            if field.name in kwargs:
                validated = field.validate(kwargs[field.name])

                if validated[1] is not None:
                    raise ActionError(validated[1])

                else:
                    req[field.name] = validated[0]

        if self.ismethod:
            rows = self.fn(args[0], self.api.db, req, self)

        else:
            rows = self.fn(self.api.db, req, self)

        return Response(rows, fields=self.response)
