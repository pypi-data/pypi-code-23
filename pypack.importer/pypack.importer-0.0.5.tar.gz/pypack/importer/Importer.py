import importlib

class Importer:

    @staticmethod
    def get (module = None, name = None):
        if not isinstance(module, str): raise TypeError('cannot import module', module)
        if not isinstance(name, str): raise TypeError('cannot import function', name)

        return getattr(importlib.import_module(module), name)

    @staticmethod
    def path (path = None, name = None):
        if not isinstance(path, str): raise TypeError('cannot import module', path)
        if not isinstance(name, str): raise TypeError('cannot import function', name)

        return importlib.machinery.SourceFileLoader(name, path).load_module()