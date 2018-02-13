import importlib

class Importer:

    @staticmethod
    def import_function (module = None, method = None):
        if not isinstance(module, str): raise TypeError('cannot import module', module)
        if not isinstance(method, str): raise TypeError('cannot import function', method)

        return getattr(importlib.import_module(module), method)