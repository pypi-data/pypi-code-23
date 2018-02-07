import re

class Route(object):
    def __init__(self, handler, details=None, **kwargs):
        self.filters = kwargs
        self.details = details
        self.handler = handler

    @property
    def pattern(self):
        if not 'hostname' in self.filters:
            return None

        pattern = '*://' + self.filters['hostname']

        if 'path' in self.filters:
            pattern += self.filters['path'] + '*' if self.filters['path'][-1] != '*' else self.filters['path']
        else:
            pattern += '/*'

        return pattern

    def pattern_matches(self, pattern, value):
        if not '*' in pattern:
            return pattern == value

        return re.match(pattern.replace('*', '.*'), value) != None

    def matches(self, request):
        if 'hostname' in self.filters and \
            not self.pattern_matches(self.filters['hostname'], request.host):
            return False
        elif 'path' in self.filters and \
            not self.pattern_matches(self.filters['path'], request.path):
            return False

        return True