from django.http import JsonResponse


class ApiResponse:

    class Pratikriyaa(JsonResponse):
        """
        Error Response Class
        """
        pass

    class SkhalitaPratikriyaa(JsonResponse):
        """
        Error Response Class
        """
        status_code = 400

        def __init__(self, data, **kwargs):
            super(ApiResponse.SkhalitaPratikriyaa, self).__init__(data, safe=False, **kwargs)

    class AsiddhauPratikriyaa(JsonResponse):
        """
        Failure Response Class
        """
        status_code = 500

        def __init__(self, data, **kwargs):
            super(ApiResponse.AsiddhauPratikriyaa, self).__init__(data, safe=False, **kwargs)

    class NotAllowedPratikriyaa(JsonResponse):
        """
                Failure Response Class
                """
        status_code = 405

        def __init__(self, data, **kwargs):
            super(ApiResponse.NotAllowedPratikriyaa, self).__init__(data, safe=False, **kwargs)

    @staticmethod
    def success(data=None, meta=None):
        pratikriyaa = {
            "status": "success",
            "data": data
        }
        if meta is not None:
            pratikriyaa["meta"] = meta
        return ApiResponse.Pratikriyaa(pratikriyaa)

    @staticmethod
    def error(message):
        pratikriyaa = {
            "status": "error",
            "data": message
        }
        return ApiResponse.SkhalitaPratikriyaa(pratikriyaa)

    @staticmethod
    def failure(failures):
        pratikriyaa = {
            "status": "failure",
            "data": failures
        }
        return ApiResponse.AsiddhauPratikriyaa(pratikriyaa)
