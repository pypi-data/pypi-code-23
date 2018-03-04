from threading import local
_thread_locals = local()


class ThreadLocal:

    @staticmethod
    def set_request(request):
        _thread_locals.request = request

    @staticmethod
    def _del_request():
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request

    @staticmethod
    def get_request():
        return _thread_locals.getattr("request")
