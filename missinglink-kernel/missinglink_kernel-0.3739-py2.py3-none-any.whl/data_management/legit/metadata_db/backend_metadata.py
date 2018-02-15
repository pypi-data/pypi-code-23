# -*- coding: utf8 -*-
import json
import logging

import requests

from ..api import default_api_retry
from ..scam import MLQueryVisitor, QueryParser, visit_query
from ..backend_mixin import BackendMixin
from .base_metadata_db import BaseMetadataDB, MetadataOperationError
from six.moves.urllib.parse import urlencode


# noinspection PyClassicStyleClass
class _VersionVisitor(MLQueryVisitor):
    def __init__(self):
        self.version = None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_version(self, node, parents=None, context=None):
        self.version = node.version


class BackendMetadataDB(BackendMixin, BaseMetadataDB):
    max_query_retry = 3

    def __init__(self, connection, config, handle_api):
        super(BackendMetadataDB, self).__init__(connection, config, handle_api)
        self.__query_parser = QueryParser()

    def _create_table(self):
        pass

    def _query_head_data(self, sha_list):
        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/metadata/head' % self._volume_id
            msg = {
                'sha': sha_list,
            }

            result = self._handle_api(
                self._config, session.post, url, msg,
                retry=default_api_retry(stop_max_attempt_number=self.max_query_retry))

            for data_item in result.get('metadata_json') or []:
                yield json.loads(data_item)

    def _add_missing_columns(self, data_object):
        pass

    def get_data_for_commit(self, sha, commit_sha):
        raise NotImplementedError(self.get_data_for_commit)

    def _add_data(self, data):
        pass

    def add_data(self, data):
        if not data:
            logging.debug('no data provided')
            return

        logging.debug('add data %s', data)

        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/metadata/head/add' % self._volume_id

            msg = {
                'metadata_url': data,
            }

            return self._handle_api(self._config, session.post, url, msg, retry=default_api_retry())

    def query(self, query_text, max_results, start_index):
        from requests_cache import CachedSession

        def _iter_data():
            for data_point in result.get('data_points') or []:
                result_data_point = {}

                for key, val in data_point.items():
                    if key == 'meta':
                        meta = result_data_point.setdefault('meta', {})
                        for meta_key_val in data_point['meta']:
                            meta[meta_key_val['key']] = meta_key_val.get('val')
                    else:
                        result_data_point[key] = val

                yield result_data_point

        version_query = query_text if query_text else '@version:head'

        tree = self.__query_parser.parse_query(query_text)

        split_visitor = _VersionVisitor()
        visit_query(split_visitor, tree)

        is_stable_version = split_visitor.version not in ['head', 'staging']

        if not is_stable_version:
            logging.info('not a stable query, caching cannot be used')

        session = CachedSession('missinglink_query') if is_stable_version else requests.session()

        with session:
            params = {
                'query': version_query
            }

            if max_results is not None:
                params['max_results'] = max_results

            if start_index is not None:
                params['start_index'] = start_index

            url = 'data_volumes/%s/query/?%s' % (self._volume_id, urlencode(params))

            result = self._handle_api(
                self._config, session.get, url, retry=default_api_retry(stop_max_attempt_number=self.max_query_retry))

            if not result['ok']:
                raise MetadataOperationError(result['error'])

            return _iter_data(), int(result.get('total_data_points', 0))

    def _query(self, sql_vars, select_fields, where, max_results, start_index):
        raise NotImplementedError(self._query)

    def get_all_data(self, sha):
        raise NotImplementedError(self.get_all_data)

    def end_commit(self):
        raise NotImplementedError(self.end_commit)

    def begin_commit(self, commit_sha, tree_id):
        raise NotImplementedError(self.begin_commit)
