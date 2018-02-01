# -*- coding: utf-8 -*-
import configparser
import sys


def load_conf(path, target=None):
    parser = configparser.ConfigParser()
    parser.read(path)
    res = {
        ("%s_%s" % (section_name, key)).upper(): value
        for section_name, section in parser.items()
        for key, value in section.items()
    }
    if target:
        target.update(res)
    else:
        return res


def write_conf(path, **values):
    parser = configparser.ConfigParser()
    parser.read(path)
    if not values:
        return
    for k, v in values.items():
        section, key = k.split("_", 1)
        if section not in parser:
            parser.add_section(section)
        parser.set(section, key, v)
    with open(path, "w") as f:
        parser.write(f)


class cached_property(object):  # noqa
    """A read only property that caches the initially computed value.

    This descriptor will only call the provided ``fget`` function once.
    Subsequent access to this property will return the cached value.

    """

    def __init__(self, fget):
        self._fget = fget

    def __get__(self, obj, cls):
        if obj is None:
            return self
        else:
            computed_value = self._fget(obj)
            obj.__dict__[self._fget.__name__] = computed_value
            return computed_value

if sys.version_info.major < 3:
    import re
    import tokenize
    import keyword

    def isidentifier(string):
        return not keyword.iskeyword(string) and re.match(tokenize.Name + '$', string)

    def mkdir(path):
        import distutils.dir_util
        distutils.dir_util.mkpath(path)
else:
    isidentifier = str.isidentifier

    def mkdir(path):
        import pathlib
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
