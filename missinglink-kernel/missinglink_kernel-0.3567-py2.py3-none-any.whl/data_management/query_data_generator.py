# -*- coding: utf8 -*-
import logging
import six
from .legit.context import build_context
from .legit.data_sync import DataSync
from .legit.data_volume import with_repo_dynamic
from .iterator import Iterator
import numpy as np
import os


class QueryDataGeneratorFactory(object):
    def __init__(self, multi_process_control, storage, data_callback, volume_id, batch_size):
        self.data_callback = data_callback
        self.volume_id = volume_id
        self.storage = storage
        self.multi_process_control = multi_process_control
        self.batch_size = batch_size

    def create(self, query):
        return QueryDataGenerator(self, query)


class MetadataIndex(object):
    def __init__(self, ctx, volume_id, query):
        self.__download_batch_size = 1000
        self._full_index = None
        self._downloaded_items_index = -1
        self.is_grouped = None
        self.download_all(ctx, volume_id, query)

    @property
    def total_items(self):
        return len(self._full_index or [])

    def __get_item(self, index):
        if index > self._downloaded_items_index:
            raise ValueError()

        return self._full_index[index]

    def get_items_flat(self, indexes):
        for i in indexes:
            items = self.__get_item(i)

            if self.is_grouped:
                for item in items:
                    yield item, i

                continue

            yield items, i

    def _add_results_using_group(self, group_key):
        def add_results(normalized_items):
            prev_metadata = (self._full_index[self._downloaded_items_index] or [{}])[0]
            prev_group_value = prev_metadata.get(group_key)

            for normalized_item in normalized_items:
                group_value = normalized_item.get(group_key)

                if prev_group_value != group_value or group_value is None:
                    self._downloaded_items_index += 1
                    self._full_index[self._downloaded_items_index] = [normalized_item]
                    prev_group_value = group_value
                else:
                    self._full_index[self._downloaded_items_index].append(normalized_item)

        return add_results

    def _add_results_individual_results(self, normalized_items):
        for normalized_item in normalized_items:
            self._downloaded_items_index += 1
            self._full_index[self._downloaded_items_index] = normalized_item

    @classmethod
    def _get_group_key_if_present(cls, query):
        from .legit.scam import QueryParser, visit_query
        from .query_visitors import GroupVisitor

        tree = QueryParser().parse_query(query)

        group_visitor = visit_query(GroupVisitor(), tree)

        return group_visitor.group

    @classmethod
    def _get_repo(cls, ctx, volume_id):
        return with_repo_dynamic(ctx, volume_id)

    def download_all(self, ctx, volume_id, query):
        logging.info('download metadata items started')

        group_key = self._get_group_key_if_present(query)
        self.is_grouped = group_key is not None
        add_results = self._add_results_using_group(group_key) if self.is_grouped else self._add_results_individual_results

        with self._get_repo(ctx, volume_id) as repo:
            data_sync = DataSync(ctx, repo, no_progressbar=True)

            data_iter = data_sync.create_download_iter(query, self.__download_batch_size)

            for normalized_items in data_iter:
                if self._full_index is None:
                    self._full_index = [None] * len(data_iter)

                add_results(normalized_items)

            if self._full_index and len(self._full_index) > self._downloaded_items_index + 1:
                self._full_index = self._full_index[:self._downloaded_items_index + 1]

        logging.info('download metadata items finished')


class QueryDataGenerator(Iterator):
    def __init__(self, creator, query):
        self._query = query
        self._creator = creator
        self._metadata_index = self._create_metadata_index(creator.volume_id, query)

        super(QueryDataGenerator, self).__init__(self._metadata_index.total_items, creator.batch_size)

    def _create_metadata_index(self, volume_id, query):
        return MetadataIndex(self.build_context(), volume_id, query)

    def _create_data_sync(self):
        ctx = self.build_context()

        with self._get_repo(ctx) as repo:
            return DataSync(ctx, repo, no_progressbar=True)

    def _get_batches_of_transformed_samples(self, index_array):
        results = self._download_data(index_array)

        batch_x = None
        batch_y = None

        def create_batch_array(obj):
            if isinstance(obj, six.integer_types + (float, )):
                return np.zeros(len(index_array), dtype=type(obj))

            return np.zeros((len(index_array),) + obj.shape, dtype=obj.dtype)

        i = 0
        for file_name, metadata in results:
            vals = self._creator.data_callback(file_name, metadata)

            if not vals or len(vals) != 2:
                logging.warning("data_callback didn't return two values (x, y)")
                continue

            x, y = vals

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
        with self.lock:
            index_array = next(self.index_generator)

        return self._get_batches_of_transformed_samples(index_array)

    @classmethod
    def build_context(cls):
        config_prefix = os.environ.get('ML_CONFIG_PREFIX')
        config_file = os.environ.get('ML_CONFIG_FILE')

        ctx = build_context(config_prefix=config_prefix, config_file=config_file)

        return ctx

    @classmethod
    def _get_repo(cls, ctx, volume_id):
        return with_repo_dynamic(ctx, volume_id)

    @classmethod
    def _group_by_index(cls, data, indices):
        results_grouped = []
        prev_index = None
        for i, d in enumerate(data):
            index = indices[i]
            if prev_index != index:
                results_grouped.append(([], []))
                prev_index = index

            results_grouped[-1][0].append(d[0])
            results_grouped[-1][1].append(d[1])

        return results_grouped

    def _download_data(self, index_array):
        ctx = self.build_context()

        with self._get_repo(ctx, self._creator.volume_id) as repo:
            data_sync = DataSync(ctx, repo, no_progressbar=True)

            results = []

            download_items_with_index = self._metadata_index.get_items_flat(index_array)
            download_items, indices = zip(*list(download_items_with_index))

            storage = self._creator.storage
            data_sync.download_items(download_items, storage, self._creator.multi_process_control)
            for normalized_item in download_items:
                full_path = storage.filename(normalized_item)
                results.append((full_path, normalized_item))

            if self._metadata_index.is_grouped:
                return self._group_by_index(results, indices)

            return results
