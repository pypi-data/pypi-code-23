# -*- coding: utf8 -*-
import os
from .legit.path_utils import safe_make_dirs
import diskcache


class RawDisk(diskcache.Disk):
    def __init__(self, directory, **kwargs):
        if 'save_meta' in kwargs:
            del kwargs['save_meta']  # workaround for old code

        directory = os.path.abspath(directory)
        super(RawDisk, self).__init__(directory, **kwargs)

    def put(self, metadata):
        key = metadata['@id']
        return super(RawDisk, self).put(key)

    def get(self, metadata, raw):
        return super(RawDisk, self).get(metadata, raw)

    def store(self, value, read, key=None):
        return super(RawDisk, self).store(value, read, key)

    def filename(self, metadata=None, value=None):
        # pylint: disable=unused-argument
        hex_name = metadata['@id']
        _, file_extension = os.path.splitext(metadata['@path'])

        sub_dir = os.path.join(hex_name[:2], hex_name[2:4])
        name = hex_name[4:] + file_extension

        filename = os.path.join(sub_dir, name)
        full_path = os.path.join(self._directory, filename)

        return filename, full_path

    def fetch(self, mode, filename, value, read):
        return super(RawDisk, self).fetch(mode, filename, value, read)


class CacheStorage(object):
    def __init__(self, cache_directory):
        self.__cache_directory = cache_directory
        self.__cache = diskcache.Cache(self.__cache_directory, disk_min_file_size=0, disk=RawDisk)

    def filename(self, metadata):
        _rel_path, full_path = self.__cache.disk.filename(metadata)
        return full_path

    def close(self):
        self.__cache.close()

    @classmethod
    def init_from_config(cls, cache_directory, **kwargs):
        return cls(cache_directory=cache_directory)

    def has_item(self, metadata):
        full_path = self.filename(metadata)
        return metadata in self.__cache and os.path.exists(full_path)

    def add_item(self, metadata, data):
        full_path = self.filename(metadata)

        dir_name = os.path.dirname(full_path)

        safe_make_dirs(dir_name)

        with open(full_path, 'wb') as f:
            f.write(data)

        if metadata not in self.__cache:
            self.__cache[metadata] = data

    @property
    def storage_params(self):
        return {
            'cache_directory': self.__cache_directory,
        }
