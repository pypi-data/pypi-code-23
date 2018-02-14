from spooler import importer


class Task(object):

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def from_name(cls, name, *args, **kwargs):
        callback = importer.find(name)
        return cls(callback, *args, **kwargs)

    def get_callback_name(self):
        return self.callback.__module__ + '.' + self.callback.__qualname__

    def execute(self):
        return self.callback(*self.args, **self.kwargs)
