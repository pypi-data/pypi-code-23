import json

from flask import make_response


def json_response(data, status_code=200):
    return make_response(json.dumps(data), status_code, {'Content-Type': 'application/json'})

class ResourceList():
    def __init__(self, resources, total_count, headers=None):
        self.headers     = headers or {}
        self.resources   = resources
        self.total_count = total_count

    def __repr__(self):
        return "ResourceList of {}/{} items".format(len(self.resources), self.total_count)
