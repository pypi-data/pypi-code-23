# -*- coding: utf8 -*-

from contextlib import closing

from .legit.path_utils import safe_make_dirs
from .legit.context import build_context
from .legit.data_sync import DataSync
from .legit.data_volume import with_repo_dynamic
from .iterator import Iterator

import numpy as np
import os
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
        return self.__cache.disk.filename(metadata)

    def close(self):
        self.__cache.close()

    @classmethod
    def init_from_config(cls, cache_directory, **kwargs):
        return cls(cache_directory=cache_directory)

    def has_item(self, metadata):
        _, full_path = self.filename(metadata)
        return metadata in self.__cache and os.path.exists(full_path)

    def add_item(self, metadata, data):
        _, full_path = self.filename(metadata)

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


class QueryDataGenerator(Iterator):
    def __init__(self, multi_process_control, cache_directory, data_callback, volume_id, query, batch_size=32, shuffle=False):
        self.data_callback = data_callback
        self.volume_id = volume_id
        self.query = query
        self.cache_directory = cache_directory
        self.multi_process_control = multi_process_control

        total_items = self.__get_query_length()
        self._full_index = [None] * total_items

        super(QueryDataGenerator, self).__init__(total_items, batch_size, shuffle=shuffle)

    def _get_batches_of_transformed_samples(self, index_array):
        results = self.__download_data(index_array)

        batch_x = None
        batch_y = None

        def create_batch_array(obj):
            if isinstance(obj, (int, float)):
                return np.zeros(len(index_array), dtype=type(obj))

            return np.zeros((len(index_array),) + obj.shape, dtype=obj.dtype)

        # build batch of image data

        i = 0
        for file_name_metadata in results:
            file_name, metadata = file_name_metadata

            x, y = self.data_callback(file_name, metadata)

            if x is None:
                continue

            if batch_x is None:
                batch_x = create_batch_array(x)

            if batch_y is None:
                batch_y = create_batch_array(y)

            batch_x[i] = x
            batch_y[i] = y

            i += 1

        return batch_x, batch_y

    def next(self):
        """For python 2.x.

        # Returns
            The next batch.
        """

        # The transformation of images is not under thread lock
        # so it can be done in parallel
        while True:
            with self.lock:
                index_array = next(self.index_generator)

            result = self._get_batches_of_transformed_samples(index_array)

            if result[0] is not None:
                return result

    @classmethod
    def build_context(cls):
        config_prefix = os.environ.get('ML_CONFIG_PREFIX')
        config_file = os.environ.get('ML_CONFIG_FILE')

        ctx = build_context(config_prefix=config_prefix, config_file=config_file)

        return ctx

    def __get_query_length(self):
        ctx = self.build_context()

        with with_repo_dynamic(ctx, self.volume_id) as repo:
            data_sync = DataSync(ctx, repo, no_progressbar=True)

            download_iter = data_sync.begin_download_iter(self.query, 0)
            next(download_iter)

            return download_iter.total_data_points

    def __download_data(self, index_array, download_batch_size=1000):
        def prepare_index_for_indexes():
            required_pages = set()

            for i in index_array:
                if self._full_index[i] is not None:
                    continue

                required_pages.add(int(i // download_batch_size))

            data_iter = data_sync.begin_download_iter(self.query, download_batch_size)

            for required_page in required_pages:
                data_iter.skip(required_page)
                page_results, _ = next(data_iter)

                for i, result in enumerate(page_results):
                    self._full_index[required_page * download_batch_size + i] = result

        ctx = self.build_context()

        def return_batch():
            result = []
            for i in index_array:
                result.append(self._full_index[i])

            yield result, None

        with closing(CacheStorage(self.cache_directory)) as storage:
            with with_repo_dynamic(ctx, self.volume_id) as repo:
                data_sync = DataSync(ctx, repo, no_progressbar=True)

                prepare_index_for_indexes()

                results = []

                for metadata in data_sync.download_iter(return_batch(), storage, self.multi_process_control):
                    _, full_path = storage.filename(metadata)
                    results.append((full_path, metadata))

                return results
