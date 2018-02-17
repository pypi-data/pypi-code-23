import json
import hashlib
import os
import logging
from copy import deepcopy

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

primitive = (int, str, bool, float)

def input_object(fn, args, kwargs):
    ret = {'args':[], 'kwargs':{}}
    for arg in args:
        arg = deepcopy(arg)
        ret['args'].append(arg)
    for arg in sorted(kwargs.keys()):
        ret['kwargs'][deepcopy(arg)] = deepcopy(kwargs[arg])
    return ret

def sha1_data(m, data):
    """
    Recursively update the SHA1 hash for list, tuple, dict and primitives.
    """
    if isinstance(data, primitive):
        m.update(str(data).encode('utf-8'))
        return
    if isinstance(data, str):
        m.update(str(data).encode('utf-8'))
        return
    if isinstance(data, tuple):
        for item in data:
            sha1_data(m, item)
        return
    if isinstance(data, list):
        for item in data:
            sha1_data(m, item)
        return
    if isinstance(data, dict):
        for key in sorted(data.keys()):
            m.update(str(key).encode('utf-8'))
            sha1_data(m, data[key])
        return
    raise Exception('Could not update sha1 for %s' % type(data))

def sha1(args, kwargs):
    """
    Calculates the SHA1 hash.
    """
    m = hashlib.sha1()
    sha1_data(m, args)
    sha1_data(m, kwargs)
    return m.hexdigest()

def cached_method(cache_path):
    """
    method decorator that memorizes the result of the function in a file in
    cache_path. The filename is based on the first argument to the method (not
    self) is hashed using sha1.
    """
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    def _cached_method_factory(fn):
        def _cached_method(*args, **kwargs):
            cache_file = cache_path + sha1(args, kwargs) + '.json'

            if not os.path.isfile(cache_file):
                logger.info('function call is not cached %s', cache_file)
                i = input_object(fn, args, kwargs)
                o = fn(*args, **kwargs)
                with open(cache_file, 'w') as f:
                    json.dump({'input':i, 'output':o}, f, indent=4)
                return o

            with open(cache_file, 'r') as f:
                logger.info('function call output is cached %s', cache_file)
                return json.load(f)['output']

        return _cached_method
    return _cached_method_factory
