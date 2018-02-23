import collections
import contextdecorator as cd
import six
import threading

modules = {}

class LocalConfig(threading.local):
    def __init__(self):
        self.stack = collections.deque([{}])

    def push(self, config):
        self.stack.appendleft(config)

    def pop(self):
        self.stack.popleft()

    def peek(self):
        try:
            return self.stack[0]
        except LookupError:
            raise LookupError("Empty config")

    def __getitem__(self, name):
        return self.peek()[name]

    def get(self, name, default=None):
        return self.peek().get(name, default)

    def __contains__(self, name):
        try:
            self[name]
        except LookupError:
            return False
        return True

config = LocalConfig()

@cd.contextmanager
def with_config(conf):
    config.push(conf)
    try:
        yield config
    finally:
        config.pop()

def use_config(config):
    config.push(config)

class Module_(object):
    def __init__(self, name):
        modules[name] = self
        self.methods = {}

    def expose(self, name=None, func=None):
        def decorator(func):
            if name is None:
                name = func.__name__
            self.methods[name] = func
        if func is None:
            return decorator
        decorator(func)

class Registry(type):
    modules = {}
    def __init__(cls, name, bases, dict_):
        try:
            Module
        except NameError:
            pass
        else:
            print(dict_)
            Registry.modules[name] = cls

@six.add_metaclass(Registry)
class Module(object):
    def __init__(self):
        self.args = config
