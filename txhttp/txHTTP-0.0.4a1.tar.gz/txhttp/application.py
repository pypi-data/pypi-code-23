from klein import Klein


class Application(Klein):
    middleware = {}

    def set_handler(self, path, handler, *args, **kwargs):
        if not hasattr(handler, '__module__') or not hasattr(handler, '__name__'):
            raise TypeError(f'Invalid handler passed.')
        kwargs.setdefault('endpoint', f'{handler.__module__}.{handler.__name__}')
        self.route(path, *args, **kwargs)(handler)

    def __getitem__(self, item):
        if item not in self.middleware:
            raise KeyError(f'Middleware {item} is not registered')
        return self.middleware[item]

    def __setitem__(self, key, value):
        self.middleware[key] = value

    def __len__(self):
        return len(self.middleware)
