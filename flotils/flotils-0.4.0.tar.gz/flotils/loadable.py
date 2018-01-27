# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
"""
Module for loading/saving data/classes with json
"""

__author__ = "the01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2013-18, Florian JUNG"
__license__ = "MIT"
__version__ = "0.3.1"
__date__ = "2018-01-27"
# Created: 2014-08-29 09:38

import os
import datetime
import json

import dateutil.parser
from dateutil.tz import tzutc
import yaml

from .logable import Logable, ModuleLogable


class Logger(ModuleLogable):
    pass


logger = Logger()
UTC = tzutc()


# TODO: New format according to https://gist.github.com/majgis/4200488
class DateTimeEncoder(json.JSONEncoder):
    """ Encode datetime, date and time objects for json """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # save all without tz info as UTC
            if obj.tzinfo:
                obj = obj.astimezone(UTC).replace(tzinfo=None)
            return {'__datetime__': obj.isoformat() + "Z"}
        elif isinstance(obj, datetime.date):
            return {'__date__': obj.isoformat()}
        elif isinstance(obj, datetime.timedelta):
            # Time delta only stores days, seconds and microseconds
            return {
                '__type__': "timedelta",
                'days': obj.days,
                'seconds': obj.seconds,
                'microseconds': obj.microseconds,
            }
        elif isinstance(obj, datetime.time):
            return {'__time__': obj.isoformat()}

        return super(DateTimeEncoder, self).default(obj)


# TODO: Load datetime as utc but without tzinfo set
class DateTimeDecoder(object):
    """ Decode datetime, date and time from json """

    @staticmethod
    def _as_datetime(dct):
        if u"__datetime__" in dct.keys():
            # Should be UTC
            return dateutil.parser.parse(
                dct['__datetime__']
            ).replace(tzinfo=UTC)
        raise TypeError("Not Datetime")

    @staticmethod
    def _as_date(dct):
        if "__date__" in dct:
            return dateutil.parser.parse(dct['__date__']).date()
        raise TypeError("Not Date")

    @staticmethod
    def _as_time(dct):
        if "__time__" in dct:
            return dateutil.parser.parse(dct['__time__']).time()
        raise TypeError("Not Time")

    @staticmethod
    def decode(dct):
        if "__type__" in dct:
            obj_type = dct.pop('__type__')

            if obj_type == "timedelta":
                return datetime.timedelta(**dct)
            # Not matched
            dct['__type__'] = obj_type

        try:
            return DateTimeDecoder._as_datetime(dct)
        except:
            try:
                return DateTimeDecoder._as_date(dct)
            except:
                try:
                    return DateTimeDecoder._as_time(dct)
                except:
                    return dct


def loadJSON(json_data, decoder=None):
    """
    Load data from json string

    :param json_data: Stringified json object
    :type json_data: str | unicode
    :param decoder: Use custom json decoder
    :type decoder: T <= DateTimeDecoder
    :return: Json data
    :rtype: None | int | float | str | list | dict
    """
    # deprecated
    import warnings
    warnings.warn(
        "This method is no longer in use - Please use load_json() instead",
        DeprecationWarning
    )
    return load_json(json_data, decoder)


def loadJSONFile(json_data, decoder=None):
    """
    Load data from json file

    :param json_data: Readable object or path to file
    :type json_data: FileIO | str
    :param decoder: Use custom json decoder
    :type decoder: T <= DateTimeDecoder
    :return: Json data
    :rtype: None | int | float | str | list | dict
    """
    # deprecated
    import warnings
    warnings.warn(
        "This method is no longer in use - Please use load_json_file() instead",
        DeprecationWarning
    )
    return load_json_file(json_data, decoder)


def saveJSON(val, pretty=False, sort=True, encoder=None):
    """
    Save data to json string

    :param val: Value or struct to save
    :type val: None | int | float | str | list | dict
    :param pretty: Format data to be readable (default: False)
                    otherwise going to be compact
    :type pretty: bool
    :param sort: Sort keys (default: True)
    :type sort: bool
    :param encoder: Use custom json encoder
    :type encoder: T <= DateTimeEncoder
    :return: The jsonified string
    :rtype: str | unicode
    """
    # deprecated
    import warnings
    warnings.warn(
        "This method is no longer in use - Please use save_json() instead",
        DeprecationWarning
    )
    return save_json(val, pretty, sort, encoder)


def saveJSONFile(
        json_data, val,
        pretty=False, compact=True, sort=True, encoder=None
):
    """
    Save data to json file

    :param json_data: Writable object or path to file
    :type json_data: FileIO | str
    :param val: Value or struct to save
    :type val: None | int | float | str | list | dict
    :param pretty: Format data to be readable (default: False)
    :type pretty: bool
    :param compact: Format data to be compact (default: True)
    :type compact: bool
    :param sort: Sort keys (default: True)
    :type sort: bool
    :param encoder: Use custom json encoder
    :type encoder: T <= DateTimeEncoder
    :rtype: None
    """
    # deprecated
    import warnings
    warnings.warn(
        "This method is no longer in use - Please use save_json_file() instead",
        DeprecationWarning
    )
    return save_json_file(json_data, val, pretty, compact, sort, encoder)


def load_json(json_data, decoder=None):
    """
    Load data from json string

    :param json_data: Stringified json object
    :type json_data: str | unicode
    :param decoder: Use custom json decoder
    :type decoder: T <= DateTimeDecoder
    :return: Json data
    :rtype: None | int | float | str | list | dict
    """
    if decoder is None:
        decoder = DateTimeDecoder
    return json.loads(json_data, object_hook=decoder.decode)


def load_json_file(json_data, decoder=None):
    """
    Load data from json file

    :param json_data: Readable object or path to file
    :type json_data: FileIO | str
    :param decoder: Use custom json decoder
    :type decoder: T <= DateTimeDecoder
    :return: Json data
    :rtype: None | int | float | str | list | dict
    """
    if decoder is None:
        decoder = DateTimeDecoder
    if not hasattr(json_data, "read"):
        with open(json_data, "rb") as f:
            return json.load(f, object_hook=decoder.decode)
    return json.load(json_data, object_hook=decoder.decode)


def save_json(val, pretty=False, sort=True, encoder=None):
    """
    Save data to json string

    :param val: Value or struct to save
    :type val: None | int | float | str | list | dict
    :param pretty: Format data to be readable (default: False)
                    otherwise going to be compact
    :type pretty: bool
    :param sort: Sort keys (default: True)
    :type sort: bool
    :param encoder: Use custom json encoder
    :type encoder: T <= DateTimeEncoder
    :return: The jsonified string
    :rtype: str | unicode
    """
    if encoder is None:
        encoder = DateTimeEncoder
    if pretty:
        return json.dumps(
            val,
            indent=4,
            separators=(',', ': '),
            sort_keys=sort,
            cls=encoder
        )
    return json.dumps(
        val,
        separators=(',', ':'),
        sort_keys=sort,
        cls=encoder
    )


def save_json_file(
        json_data, val,
        pretty=False, compact=True, sort=True, encoder=None
):
    """
    Save data to json file

    :param json_data: Writable object or path to file
    :type json_data: FileIO | str
    :param val: Value or struct to save
    :type val: None | int | float | str | list | dict
    :param pretty: Format data to be readable (default: False)
    :type pretty: bool
    :param compact: Format data to be compact (default: True)
    :type compact: bool
    :param sort: Sort keys (default: True)
    :type sort: bool
    :param encoder: Use custom json encoder
    :type encoder: T <= DateTimeEncoder
    :rtype: None
    """
    # TODO: make pretty/compact into one bool?
    if encoder is None:
        encoder = DateTimeEncoder
    opened = False

    if not hasattr(json_data, "write"):
        json_data = open(json_data, "wb")
        opened = True

    try:
        if pretty:
            json.dump(
                val,
                json_data,
                indent=4,
                separators=(',', ': '),
                sort_keys=sort,
                cls=encoder
            )
        elif compact:
            json.dump(
                val,
                json_data,
                separators=(',', ':'),
                sort_keys=sort,
                cls=encoder
            )
        else:
            json.dump(val, json_data, sort_keys=sort, cls=encoder)
    finally:
        if opened:
            json_data.close()

def load_yaml(data):
    """
    Load data from yaml string

    :param data: Stringified yaml object
    :type data: str | unicode
    :return: Yaml data
    :rtype: None | int | float | str | unicode | list | dict
    """
    return yaml.load(data)


def load_yaml_file(data):
    """
    Load data from yaml file

    :param json_data: Readable object or path to file
    :type json_data: FileIO | str | unicode
    :return: Yaml data
    :rtype: None | int | float | str | unicode | list | dict
    """
    if not hasattr(data, "read"):
        with open(data, "rb") as f:
            return yaml.load(f)
    return yaml.load(data)


def save_yaml(val):
    """
    Save data to yaml string

    :param val: Value or struct to save
    :type val: None | int | float | str | unicode | list | dict
    :return: The yamlified string
    :rtype: str | unicode
    """
    return yaml.dump(val)


def save_yaml_file(yaml_data, val):
    """
    Save data to yaml file

    :param yaml_data: Writable object or path to file
    :type yaml_data: FileIO | str | unicode
    :param val: Value or struct to save
    :type val: None | int | float | str | unicode | list | dict
    """
    opened = False

    if not hasattr(yaml_data, "write"):
        yaml_data = open(yaml_data, "wb")
        opened = True

    try:
        yaml.dump(val, yaml_data)
    finally:
        if opened:
            yaml_data.close()


def load_file(path):
    """
    Load file

    :param path: Path to file
    :type path: str | unicode
    :return: Loaded data
    :rtype: None | int | float | str | unicode | list | dict
    :raises IOError: If file not found or error accessing file
    """
    res = {}

    if not path:
        IOError("No path specified to save")

    if not os.path.isfile(path):
        raise IOError("File not found {}".format(path))

    try:
        with open(path, "rb") as f:
            if path.endswith(".json"):
                res = load_json_file(f)
            elif path.endswith(".yaml") or path.endswith(".yml"):
                res = load_yaml_file(f)
    except IOError:
        raise
    except Exception as e:
        raise IOError(e)
    return res


def save_file(path, data, readable=False):
    """
    Save to file

    :param path: File path to save
    :type path: str | unicode
    :param data: Data to save
    :type data: None | int | float | str | unicode | list | dict
    :param readable: Format file to be human readable (default: False)
    :type readable: bool
    :rtype: None
    :raises IOError: If empty path or error writing file
    """
    if not path:
        IOError("No path specified to save")

    try:
        with open(path, "wb") as f:
            if path.endswith(".json"):
                save_json_file(
                    f,
                    data,
                    pretty=readable,
                    compact=(not readable),
                    sort=True
                )
            elif path.endswith(".yaml") or path.endswith(".yml"):
                save_yaml_file(f, data)
    except IOError:
        raise
    except Exception as e:
        raise IOError(e)


def joinPathPrefix(path, pre_path=None):
    """
        If path set and not absolute, append it to pre path (if used)

        :param path: path to append
        :type path: str | None
        :param pre_path: Base path to append to (default: None)
        :type pre_path: None | str
        :return: Path or appended path
        :rtype: str | None
        """
    # deprecated
    import warnings
    warnings.warn(
        "This method is no longer in use - Please use join_path_prefix() instead",
        DeprecationWarning
    )
    return join_path_prefix(path, pre_path)


def join_path_prefix(path, pre_path=None):
    """
        If path set and not absolute, append it to pre path (if used)

        :param path: path to append
        :type path: str | None
        :param pre_path: Base path to append to (default: None)
        :type pre_path: None | str
        :return: Path or appended path
        :rtype: str | None
        """
    if not path:
        return path

    if pre_path and not os.path.isabs(path):
        return os.path.join(pre_path, path)

    return path


class Loadable(Logable):
    """
    Class to facilitate loading config from json-files and ease relative paths
    """

    def __init__(self, settings=None):
        """
        Initialize object

        :param settings: Settings for instance (default: None)
        :type settings: dict | None
        :rtype: None
        :raises IOError: Failed to load settings file
        """
        if settings is None:
            settings = {}
        super(Loadable, self).__init__(settings)
        sett_path = settings.get('settings_file', None)
        self._prePath = settings.get('path_prefix', None)

        if sett_path:
            sett_path = self.join_path_prefix(sett_path)
            sett = self.load_settings(sett_path)
            sett_prepath = sett.get('path_prefix')
            if sett_prepath:
                # if settPath is absolute path
                # -> set to settPath else join with dict path_prefix
                self._prePath = self.join_path_prefix(sett_prepath)
            # settings in constructor overwrite settings from file
            sett.update(settings)
            settings.update(sett)
            self.debug("Loaded config {}".format(sett_path))
            # to apply loaded settings to logable as well
            super(Loadable, self).__init__(settings)

    def joinPathPrefix(self, path):
        """
        If path set and not absolute, append it to self._prePath

        :param path: Path to append
        :type path: str | None
        :return: Path or appended path
        :rtype: str | None
        """
        import warnings
        warnings.warn(
            "This method is no longer in use - Please use .join_path_prefix() instead",
            DeprecationWarning
        )
        return self.join_path_prefix(path)

    def join_path_prefix(self, path):
        """
        If path set and not absolute, append it to self._prePath

        :param path: Path to append
        :type path: str | None
        :return: Path or appended path
        :rtype: str | None
        """
        return join_path_prefix(path, self._prePath)

    def _loadJSONFile(self, json_data, decoder=None):
        """
        Load data from json file

        :param json_data: Readable file or path to file
        :type json_data: FileIO | str
        :param decoder: Use custom json decoder
        :type decoder: T <= DateTimeDecoder
        :return: Json data
        :rtype: None | int | float | str | list | dict
        :raises IOError: Failed to load
        """
        import warnings
        warnings.warn(
            "This method is no longer in use - Please use ._load_json_file() instead",
            DeprecationWarning
        )
        return self._load_json_file(json_data, decoder)

    def _load_json_file(self, json_data, decoder=None):
        """
        Load data from json file

        :param json_data: Readable file or path to file
        :type json_data: FileIO | str
        :param decoder: Use custom json decoder
        :type decoder: T <= DateTimeDecoder
        :return: Json data
        :rtype: None | int | float | str | list | dict
        :raises IOError: Failed to load
        """
        try:
            res = load_json_file(json_data, decoder=decoder)
        except ValueError as e:
            if "{}".format(e) == "No JSON object could be decoded":
                raise IOError("Decoding JSON failed")
            self.exception(u"Failed to load from {}".format(json_data))
            raise IOError("Loading file failed")
        except:
            self.exception(u"Failed to load from {}".format(json_data))
            raise IOError("Loading file failed")
        return res

    def _saveJSONFile(self, json_data, val,
                      pretty=False, compact=True, sort=True, encoder=None
    ):
        """
        Save data to json file

        :param json_data: Writable file or path to file
        :type json_data: FileIO | str
        :param val: Value or struct to save
        :type val: None | int | float | str | list | dict
        :param pretty: Format data to be readable (default: False)
        :type pretty: bool
        :param compact: Format data to be compact (default: True)
        :type compact: bool
        :param sort: Sort keys (default: True)
        :type sort: bool
        :param encoder: Use custom json encoder
        :type encoder: T <= DateTimeEncoder
        :rtype: None
        :raises IOError: Failed to save
        """
        import warnings
        warnings.warn(
            "This method is no longer in use - Please use ._save_json_file() instead",
            DeprecationWarning
        )
        return self._save_json_file(json_data, val, pretty, compact, sort, encoder)

    def _save_json_file(self, json_data, val,
                      pretty=False, compact=True, sort=True, encoder=None
    ):
        """
        Save data to json file

        :param json_data: Writable file or path to file
        :type json_data: FileIO | str
        :param val: Value or struct to save
        :type val: None | int | float | str | list | dict
        :param pretty: Format data to be readable (default: False)
        :type pretty: bool
        :param compact: Format data to be compact (default: True)
        :type compact: bool
        :param sort: Sort keys (default: True)
        :type sort: bool
        :param encoder: Use custom json encoder
        :type encoder: T <= DateTimeEncoder
        :rtype: None
        :raises IOError: Failed to save
        """
        try:
            save_json_file(json_data, val, pretty, compact, sort, encoder)
        except:
            self.exception(u"Failed to save to {}".format(json_data))
            raise IOError("Saving file failed")

    def _load_yaml_file(self, data):
        """
        Load data from yaml file

        :param data: Readable object or path to file
        :type data: FileIO | str | unicode
        :return: Yaml data
        :rtype: None | int | float | str | unicode | list | dict
        :raises IOError: Failed to load
        """
        try:
            res = load_yaml_file(data)
        except:
            self.exception(u"Failed to load from {}".format(data))
            raise IOError("Loading file failed")
        return res

    def _save_yaml_file(self, yaml_data, val):
        """
        Save data to yaml file

        :param yaml_data: Writable object or path to file
        :type yaml_data: FileIO | str | unicode
        :param val: Value or struct to save
        :type val: None | int | float | str | unicode | list | dict
        :raises IOError: Failed to save
        """
        try:
            save_yaml_file(yaml_data, val)
        except:
            self.exception(u"Failed to save to {}".format(yaml_data))
            raise IOError("Saving file failed")

    def loadSettings(self, path):
        """
        Load settings dict

        :param path: Path to settings file
        :type path: str | unicode
        :return: Loaded settings
        :rtype: dict
        :raises IOError: If file not found or error accessing file
        :raises TypeError: Settings file does not contain dict
        """
        import warnings
        warnings.warn(
            "This method is no longer in use - Please use .load_settings() instead",
            DeprecationWarning
        )
        return self.load_settings(path)

    def load_settings(self, path):
        """
        Load settings dict

        :param path: Path to settings file
        :type path: str | unicode
        :return: Loaded settings
        :rtype: dict
        :raises IOError: If file not found or error accessing file
        :raises TypeError: Settings file does not contain dict
        """
        res = self.load_file(path)
        if not isinstance(res, dict):
            raise TypeError("Expected settings to be dict")
        return res

    def saveSettings(self, path, settings, readable=False):
        """
        Save settings to file

        :param path: File path to save
        :type path: str | unicode
        :param settings: Settings to save
        :type settings: dict
        :param readable: Format file to be human readable (default: False)
        :type readable: bool
        :rtype: None
        :raises IOError: If empty path or error writing file
        :raises TypeError: Settings is not a dict
        """
        import warnings
        warnings.warn(
            "This method is no longer in use - Please use .save_settings() instead",
            DeprecationWarning
        )
        return self.save_settings(path, settings, readable)

    def save_settings(self, path, settings, readable=False):
        """
        Save settings to file

        :param path: File path to save
        :type path: str | unicode
        :param settings: Settings to save
        :type settings: dict
        :param readable: Format file to be human readable (default: False)
        :type readable: bool
        :rtype: None
        :raises IOError: If empty path or error writing file
        :raises TypeError: Settings is not a dict
        """
        if not isinstance(settings, dict):
            raise TypeError("Expected settings to be dict")
        return self.save_file(path, settings, readable)

    def load_file(self, path):
        """
        Load file

        :param path: Path to file
        :type path: str | unicode
        :return: Loaded settings
        :rtype: None | str | unicode | int | list | dict
        :raises IOError: If file not found or error accessing file
        """
        res = None

        if not path:
            IOError("No path specified to save")

        if not os.path.isfile(path):
            raise IOError("File not found {}".format(path))

        try:
            with open(path, "rb") as f:
                if path.endswith(".json"):
                    res = self._load_json_file(f)
                elif path.endswith(".yaml") or path.endswith(".yml"):
                    res = self._load_yaml_file(f)
        except IOError:
            raise
        except Exception as e:
            self.exception("Failed reading {}".format(path))
            raise IOError(e)
        return res

    def save_file(self, path, data, readable=False):
        """
        Save to file

        :param path: File path to save
        :type path: str | unicode
        :param data: To save
        :type data: None | str | unicode | int | list | dict
        :param readable: Format file to be human readable (default: False)
        :type readable: bool
        :rtype: None
        :raises IOError: If empty path or error writing file
        """
        if not path:
            IOError("No path specified to save")

        try:
            with open(path, "wb") as f:
                if path.endswith(".json"):
                    self._save_json_file(
                        f,
                        data,
                        pretty=readable,
                        compact=(not readable),
                        sort=True
                    )
                elif path.endswith(".yaml") or path.endswith(".yml"):
                    self._save_yaml_file(f, data)
        except IOError:
            raise
        except Exception as e:
            self.exception("Failed writing {}".format(path))
            raise IOError(e)
