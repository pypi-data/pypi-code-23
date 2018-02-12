"""
text helper utils for hrjota
"""
import json
import datetime


# this allows us to use datetime in json dumps
json.JSONEncoder.default = lambda self, obj: (
    obj.isoformat() if isinstance(obj, datetime.datetime) else None
)


def jsond(data, sort=True, indent=2):
    """dumps a pretty looking json of the data"""
    return json.dumps(data, sort_keys=sort, indent=indent)
