

class ModuleProxy(object):

    def __init__(self, name):
        self.name = name
        self.module = None

    def _load_module(self):
        if not self.module:
            import importlib
            self.module = importlib.import_module(self.name, __package__)

    def __getattr__(self, item):
        self._load_module()
        return getattr(self.module, item)

rook_pb2 = ModuleProxy('.python.rook_pb2')
rook_pb2_grpc = ModuleProxy('.python.rook_pb2_grpc')
