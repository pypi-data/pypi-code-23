from setuptools import setup
from json import load


def convert(input):
    if isinstance(input, dict):
        return {convert(k): convert(v) for k, v in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode("utf-8")
    else:
        return input

with open("package.json") as config_file:
    config = load(config_file, object_hook=convert)
    config.pop("version_hash")
    setup(**config)
