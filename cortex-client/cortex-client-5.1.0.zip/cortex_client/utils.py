import json
import logging

def get_logger(name):
    log = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s/%(module)s: %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log

def json_str(val):
    try:
        return json.dumps(val)
    except TypeError:
        return str(val)
