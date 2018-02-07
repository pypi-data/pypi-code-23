from collections import namedtuple


config_types = {}
ConfigType = namedtuple('ConfigType', ['func', 'name', 'user_friendly_name', 'is_unique'])


class register_config:

    def __init__(self, name, user_friendly_name, is_unique=False, call_on_save=True):
        self.name = name
        self.user_friendly_name = user_friendly_name
        self.is_unique = is_unique

    def __call__(self, func):
        config_types[self.name] = ConfigType(func, self.name, self.user_friendly_name, self.is_unique)

