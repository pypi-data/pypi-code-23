import logging
from rest_framework.response import Response


logger = logging.getLogger(__name__)


class JsonResponse(Response):
    def __init__(self, code=0, msg=None, data=None):
        data = {'code': code,
                'msg': msg,
                'data': data}
        return super().__init__(data, status=200)


class ObjectDosNotExistResponse(JsonResponse):
    def __init__(self, code=10, msg="Object does not exist", data=None):
        return super().__init__(code, msg, data)


class FormMissResponse(JsonResponse):
    def __init__(self, code=11, msg="Insufficient form fields", data=None):
        return super().__init__(code, msg, data)


class ExcelWrongFormatResponse(JsonResponse):
    def __init__(self, code=12,
                 msg="Excel file's format incorrent",
                 data=None):
        return super().__init__(code, msg, data)
