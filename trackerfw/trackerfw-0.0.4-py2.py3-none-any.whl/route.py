import re

class Route(object):
    def __init__(self, route, handler, details):
        self.route = route
        self.details = details
        self.handler = handler

    @property
    def match_pattern(self):
        pattern = '*://' + self.route

        if pattern[-1] != '*':
            return pattern + '*'

        return pattern

    def matches(self, uri):
        return re.match('.*:\/\/' + self.route.replace('/', '\\/').replace('*', '.*'), uri) != None