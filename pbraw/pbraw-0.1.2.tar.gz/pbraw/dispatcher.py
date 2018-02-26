from pbraw.util import get_url

class URLDispatcher():

    def __init__(self):
        if hasattr(self, 'instance') and self.instance:
            return
        self.handlers = []
        URLDispatcher.instance = self

    class handler():

        class _handler():
            def __init__(self, handler, priority):
                self.handler = handler
                URLDispatcher.instance.register_handler(handler, priority)

            def __call__(self, *args):
                return self.handler(*args)

        def __init__(self, priority=100, *args, **kwargs):
            self.priority = priority

        def __call__(self, func, *args, **kwargs):
            x = self._handler(func, self.priority)
            return x

    def register_handler(self, handler, priority):
        i = 0
        for i in range(len(self.handlers)):
            if self.handlers[i][0] > priority:
                break

        self.handlers.insert(i, (priority, handler))

    def grab_url(self, url):
        req = get_url(url)
        if not req:
            return []
        for (priority, handler) in self.handlers:
            res = handler(url, req)
            if res:
                return res
        return []
