import asyncio
from json import JSONDecodeError

from aiohttp import hdrs
from puer.views import View, Response

from ..exceptions import APIInvalidJSONError, APIBadRequest

__all__ = ["APIView"]


class APIView(View):
    """
    Base REST view with check request data by marshmallow schema (see Meta.data_schema)
    """

    serializer = None

    def __init__(self, request):
        super().__init__(request)
        self.raw_data = {}
        self.validated_data = {}

    def _raise_allowed_methods(self):
        allowed_methods = {
            m for m in hdrs.METH_ALL if hasattr(self, m.lower())}
        raise APIBadRequest()

    @asyncio.coroutine
    def __iter__(self):
        # Check for allowed method
        if self.request._method not in hdrs.METH_ALL:
            self._raise_allowed_methods()

        # Dispatch http method
        resp = yield from self.dispatch()
        return resp

    def get_serializer(self):
        return self.serializer(context={"request": self.request})

    def get_method(self):
        return self.request._method.lower()
        
    async def dispatch(self):
        # Check content_type for application/json, get dict from request JSON
        method_name = self.get_method()
        if method_name is None:
            self._raise_allowed_methods()
        method = getattr(self, method_name, None)
        if method is None:
            self._raise_allowed_methods()

        content_type = self.request.headers.get("Content-Type")
        if self.request._method.lower() not in ('get', 'delete', 'options'):
            if content_type == "application/json":
                try:
                    self.raw_data = await self.request.json()
                except JSONDecodeError:
                    raise APIInvalidJSONError()
                # Data validation
                if self.get_serializer() is not None:
                    self.validate_data()
            else:
                raise APIInvalidJSONError()
        return await method()

    def validate_data(self):
        serializer = self.get_serializer()
        marshmallow_result = serializer.load(self.raw_data)
        errors = marshmallow_result.errors
        if any(errors):
            raise APIBadRequest({"fields": errors})
        self.validated_data = marshmallow_result.data

    async def options(self):
        return Response()

        

