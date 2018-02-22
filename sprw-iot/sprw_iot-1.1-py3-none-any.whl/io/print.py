from pprint import pprint
import datetime
from collections import OrderedDict
import json
from .config import Config

def iotprint(data):

    """Prints python data structures in a neatly formatted manner.

        Parameters:
            data: Data to be printed

        Example:
            The following example shows how to use iotprint::
            
                led_thing = sp_server.get_thing(2)
                iotprint(led_thing)
            
            **Expected Output**::

                {
                    "attributes": {
                        "pin_number": "2"
                    },
                    "category": "INPUT_DEVICE",
                    "created_at": {
                        "date": "2017-12-29 13:16:34.000000",
                        "timezone": "UTC",
                        "timezone_type": 3
                    },
                    "description": null,
                    "desired_state": {
                        "value": 0
                    },
                    "device": "BUTTON",
                    "id": 20,
                    "name": "My Switch",
                    "reported_state": {
                        "value": 0
                    },
                    "updated_at": {
                        "date": "2017-12-29 13:16:34.000000",
                        "timezone": "UTC",
                        "timezone_type": 3
                    }
                }


    """
    dict_data = __convert_to_dict(data)
    print(json.dumps(dict_data, indent=4, sort_keys=True))

def __convert_to_dict(obj):
    if hasattr(obj, "_asdict"):  # detect namedtuple
        return OrderedDict(zip(obj._fields, (__convert_to_dict(item) for item in obj)))
    elif isinstance(obj, str):  # iterables - strings
        return obj
    elif hasattr(obj, "keys"):  # iterables - mapping
        return OrderedDict(zip(obj.keys(), (__convert_to_dict(item) for item in obj.values())))
    elif hasattr(obj, "__iter__"):  # iterables - sequence
        return type(obj)((__convert_to_dict(item) for item in obj))
    elif isinstance(obj, datetime.datetime):
        return datetime.datetime.strftime(obj, Config.datetime_format)
    else:  # non-iterable cannot contain namedtuples
        return obj
