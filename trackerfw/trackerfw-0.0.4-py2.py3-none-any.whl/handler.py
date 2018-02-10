from abc import ABCMeta, abstractmethod

class Handler(object, metaclass=ABCMeta):
    def __init__(self, server):
        self.server = server

    def setup(self):
        pass

    async def shutdown(self):
        pass

    @abstractmethod
    async def dispatch(self, request):
        return
