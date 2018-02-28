import re


class PatternDict:
    """
    In-memory dictionary of compiled patterns
    """
    __slots__ = ('patterns', )

    def compile_all(self):
        for pattern_name, pattern_value in self.patterns.items():
            if isinstance(pattern_value, str):
                self.patterns[pattern_name] = re.compile(pattern_value)

    def __init__(self, patterns: dict = None):
        self.patterns = patterns or {}
        self.compile_all()

    def __setitem__(self, key, value):
        if isinstance(value, str):
            value = re.compile(value)
        return self.patterns.__setitem__(key, value)

    def __delitem__(self, key):  # pragma: nocover
        return self.patterns.__delitem__(key)

    def __contains__(self, item):
        return self.patterns.__contains__(item)

    def __getitem__(self, item):
        return self.patterns.__getitem__(item)

    def __len__(self):  # pragma: nocover
        return self.patterns.__len__()

    def __iter__(self):  # pragma: nocover
        return self.patterns.__iter__()

    def update(self, dic: dict):
        self.patterns.update(dic)
        self.compile_all()
