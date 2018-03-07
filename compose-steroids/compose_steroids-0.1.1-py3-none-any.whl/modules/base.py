import inspect


class Base:

    def __init__(self, **kwargs):
        attributes = [
            (name, default_value)
            for name, default_value in inspect.getmembers(self)
            if not name.startswith('__') and not callable(default_value)
        ]
        for name, default_value in attributes:
            try:
                value = kwargs.pop(name)
            except KeyError:
                setattr(self, name, default_value)
            else:
                setattr(self, name, value)
        super().__init__()

    def run(self, compose):
        pass
