from __future__ import absolute_import

from json import JSONEncoder, JSONDecoder, loads
from json.decoder import WHITESPACE

class MongoDBJSONEncoder(JSONEncoder):

    def default(self, o):
        return super(MongoDBJSONEncoder, self).default(self, o)

class MongoDBJSONDecoder(JSONDecoder):

    def decode(self, s, _w=WHITESPACE.match):
        return super(MongoDBJSONDecoder, self).decode(s)

def decode(s):
    return loads(s, cls=MongoDBJSONDecoder)
