import importlib

class Importer:

    @staticmethod
    def get (module = None, name = None):
        if not isinstance(module, str): raise TypeError('cannot import module', module)
        if not isinstance(name, str): raise TypeError('cannot import function', name)

        return getattr(importlib.import_module(module), name)