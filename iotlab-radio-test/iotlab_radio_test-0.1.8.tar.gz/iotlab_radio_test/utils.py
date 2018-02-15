import collections

import os

import numpy as np


def merge(obj, other, attrs):
    for k in attrs:
        other_val = getattr(other, k)
        if other_val:
            setattr(obj, k, other_val)


class ComparableMixin(object):
    def _compare(self, other, method):
        try:
            return method(self._cmpkey(), other._cmpkey())
        except (AttributeError, TypeError):
            # _cmpkey not implemented, or return different type,
            # so I can't compare with "other".
            return NotImplemented

    def __lt__(self, other):
        return self._compare(other, lambda s,o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s,o: s <= o)

    def __eq__(self, other):
       return self._compare(other, lambda s,o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s,o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s,o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s,o: s != o)


class BaseConfig(ComparableMixin):
    __attrs__ = []

    def merge(self, other):
        merge(self, other, self.__attrs__)
        return self

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__attrs__}

    def _cmpkey(self):
        return tuple(self.__dict__.values())


class RadioConfig(BaseConfig):
    __attrs__ = ['packet_size', 'packet_numbers',
                 'packet_interval', 'channel_list',
                 'txpower_list']

    def __init__(self, packet_size=None, packet_numbers=None,
                 packet_interval=None, channel_list=None,
                 txpower_list=None):
        self.packet_size = packet_size
        self.packet_numbers = packet_numbers
        self.packet_interval = packet_interval
        self.channel_list = channel_list
        self.txpower_list = txpower_list


class DrawConfig(BaseConfig):
    __attrs__ = ['elev', 'azim',
                 'font_size', 'robots',
                 'wifi']

    def __init__(self, elev=None, azim=None,
                 font_size=None, robots=None,
                 wifi=None):
        self.elev = elev
        self.azim = azim
        self.font_size = font_size
        if robots is None:
            robots = []
        self.robots = robots
        if wifi is None:
            wifi = []
        self.wifi = wifi


class Config(BaseConfig):
    __attrs__ = ['site', 'archi', 'node_list', 'duration']

    def __init__(self, site=None, archi=None,
                 node_list=None, duration=None,
                 radio=None, draw=None):
        self.site = site
        self.archi = archi
        self.node_list = node_list
        self.duration = duration
        self.radio = radio
        self.draw = draw


    def to_dict(self):
        asdict = BaseConfig.to_dict(self)
        asdict['radio'] = self.radio.to_dict()
        asdict['draw'] = self.draw.to_dict()
        return asdict

    def merge(self, other):
        merged = BaseConfig.merge(self, other)
        merged.radio.merge(other.radio)
        merged.draw.merge(other.draw)
        return merged

    @classmethod
    def from_dict(cls, input_dict):
        obj = cls(**input_dict)
        obj.radio = RadioConfig(**input_dict.get('radio', {}))
        obj.draw = DrawConfig(**input_dict.get('draw', {}))
        return obj


def get_or_create_dir(directory, create):
    if not os.path.exists(directory) and create:
        os.makedirs(directory)
    return directory


# https://stackoverflow.com/a/6037657
def unflatten(dictionary, sep='.'):
    result_dict = {}
    for key, value in dictionary.iteritems():
        parts = key.split(sep)
        new_dict = result_dict
        for part in parts[:-1]:
            if part not in new_dict:
                new_dict[part] = {}
            new_dict = new_dict[part]
        new_dict[parts[-1]] = value
    return result_dict


# https://stackoverflow.com/a/6027615
def flatten(input_dict, parent_key='', sep='.'):
    items = []
    for key, value in input_dict.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def string_represents_integer(input_str):
    try:
        int(input_str)
        return True
    except ValueError:
        return False


def yes_no(answer):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    while True:
        choice = raw_input(answer + ' [y/n]').lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print "Please respond with 'yes' or 'no'\n"


def save_csv(full_path, data):
    np.savetxt(full_path, data, delimiter=",", fmt="%d")

