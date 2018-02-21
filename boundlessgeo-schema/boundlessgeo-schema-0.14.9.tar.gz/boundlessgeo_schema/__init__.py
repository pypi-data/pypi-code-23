try:
    import _pickle as pickle
except ImportError:
    import cPickle as pickle
from os.path import abspath, dirname, join


def get_schema():
    with open(join(dirname(abspath(__file__)), 'actions.p'), 'rb') as fp:
        schema = pickle.load(fp)

    return schema


def get_events():
    with open(join(dirname(abspath(__file__)), 'events.p'), 'rb') as fp:
        events = pickle.load(fp)

    return events


def get_version():
    schema = get_schema()
    version = schema['_version']

    return version


__version__ = get_version()
