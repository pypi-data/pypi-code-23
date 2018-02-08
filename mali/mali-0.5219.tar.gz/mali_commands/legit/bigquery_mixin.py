# -*- coding: utf8 -*-
import logging
import os
from uuid import uuid4

from .job import Job
from .connection_mixin import ConnectionMixin


class BqJob(Job):
    def __init__(self, job, result_callback=None):
        self.__job = job
        self.__result_callback = result_callback

    def wait(self):
        result = self.__job.result()

        logging.info('bq job result %s', result)

        return self.__result_callback(result) if self.__result_callback else result


class BigQueryMixin(ConnectionMixin):
    def _query_async(self, query, job_config=None):
        from google.cloud.bigquery import QueryJobConfig

        job_config = job_config or QueryJobConfig()
        debug_params = [param.to_api_repr() for param in job_config.query_parameters]
        logging.info('query async: %s, params: %s, legacy_sql: %s', query, debug_params, job_config.use_legacy_sql)

        if job_config.use_query_cache is None:
            job_config.use_query_cache = True

        bq_client = self._connection

        return bq_client.query(query, job_config)

    def __return_results_iter(self, table, selected_fields, max_results, start_index, process_row):
        bq_client = self._connection

        results_iter = bq_client.list_rows(
            table, selected_fields=selected_fields, max_results=max_results, start_index=start_index)

        return self.__return_results_from_iter(results_iter, max_results, process_row, selected_fields)

    @classmethod
    def __return_results_from_iter_up_to(cls, results_iter, total_left, process_row, schema):
        for result in results_iter:
            if total_left == 0:
                return

            if process_row is not None:
                yield process_row(result, schema)
            else:
                yield result

            total_left -= 1

    @classmethod
    def __return_results_from_iter(cls, results_iter, max_results, process_row, schema):
        total_left = max_results

        if total_left is None:
            total_left = -1

        if total_left == 0:
            return

        for result in cls.__return_results_from_iter_up_to(results_iter, total_left, process_row, schema):
            yield result

    def _query_sync(self, query, job_config, max_results=None, start_index=0, process_row=None):
        query_job = self._query_async(query, job_config)
        results_iter = query_job.result()

        query_results = query_job.query_results()

        # noinspection PyProtectedMember
        logging.debug('query results %s', query_results._properties)

        def direct_data_enum():
            return self.__return_results_from_iter(results_iter, max_results, process_row, query_results.schema)

        def table_data_enum():
            return self.__return_results_iter(
                query_job.destination, query_results.schema, max_results, start_index, process_row)

        def return_empty_result():
            return []

        if query_results.total_rows > 0:
            data_enum = direct_data_enum if max_results is None and start_index == 0 else table_data_enum
        else:
            data_enum = return_empty_result

        return data_enum(), query_results.total_rows

    @classmethod
    def valid_table_name_random_token(cls, size=8):
        from base58 import b58encode

        return b58encode(os.urandom(size))

    @classmethod
    def _get_table_name(cls, prefix, name):
        table_full_name = '{prefix}_{name}'.format(prefix=prefix, name=name)

        return table_full_name

    def _get_table_ref(self, name):
        table_full_name = self._get_table_name(self._connection.table_prefix, name)

        with self._connection.get_cursor() as bq_dataset:
            return bq_dataset.table(table_full_name)

    def _create_specific_table(self, name, schema):
        logging.info('create_specific_table %s with schema %s', name, schema)

        import google.cloud.exceptions
        from google.cloud.bigquery import Table

        table_ref = self._get_table_ref(name)

        table = Table(table_ref, schema=schema)

        bq_client = self._connection

        try:
            bq_client.create_table(table)
        except google.cloud.exceptions.Conflict:
            table = self._get_specific_table(name)

        return table

    def _get_specific_table(self, name):
        table_ref = self._get_table_ref(name)

        bq_client = self._connection

        return bq_client.get_table(table_ref)

    def _copy_table_data(self, src_query, src_query_params, dest_table_ref, write_disposition=None):
        return self._async_copy_table_data(src_query, src_query_params, dest_table_ref, write_disposition).result()

    def _async_copy_table_data(self, src_query, src_query_params, dest_table_ref, write_disposition=None):
        from google.cloud.bigquery.job import WriteDisposition
        from google.cloud.bigquery import QueryJobConfig

        write_disposition = write_disposition or WriteDisposition.WRITE_APPEND

        logging.info(
            'copy_table_data to %s filter query: %s params: %s (%s)',
            dest_table_ref.table_id if dest_table_ref else '(random table)', src_query, src_query_params, write_disposition)

        job_config = QueryJobConfig()
        job_config.query_parameters = src_query_params
        job_config.destination = dest_table_ref
        job_config.write_disposition = write_disposition

        return self._query_async(src_query, job_config)

    def _extract_table(self, table_ref, url):
        from google.cloud.bigquery.job import DestinationFormat
        from google.cloud.bigquery import ExtractJobConfig

        logging.info('extract_table %s to %s', table_ref.table_id, url)

        job_config = ExtractJobConfig()
        if url.endswith('.json'):
            job_config.destination_format = DestinationFormat.NEWLINE_DELIMITED_JSON

        bq_client = self._connection

        return bq_client.extract_table(table_ref, url, job_config=job_config)

    def _async_load_job(self, url, schema=None):
        from google.cloud.bigquery import LoadJobConfig
        from google.cloud.bigquery.job import DestinationFormat

        job_config = LoadJobConfig()
        if url.endswith('.json'):
            job_config.source_format = DestinationFormat.NEWLINE_DELIMITED_JSON

        job_config.autodetect = schema is None
        if schema is not None:
            job_config.schema = schema

        bq_client = self._connection

        dest_table_ref = self._get_table_ref(uuid4().hex)

        return bq_client.load_table_from_uri(url, dest_table_ref, job_config=job_config)

    @classmethod
    def bq_field_name_to_common_name(cls, name):
        return '@' + name[1:] if name in ['_commit_sha', '_size', '_sha', '_hash', '_url', '_phase'] else name

    @classmethod
    def common_name_to_bq_field_name(cls, name):
        return '_' + name[1:] if name.startswith('@') else name

    @classmethod
    def build_dict(cls, row, schema):
        return {
            cls.bq_field_name_to_common_name(field.name): val for field, val in zip(schema, row) if val is not None
        }

    def _return_async_scalar(self, query, name):
        from google.cloud.bigquery import QueryJobConfig

        job_config = QueryJobConfig()

        job = self._query_async(query, job_config)

        def process_result(results):
            for result in results:
                return result[name]

        return BqJob(job, process_result)

    @classmethod
    def _get_fields_schema(cls, new_staging_fields, table):
        for field in table.schema:
            if field.name in new_staging_fields:
                yield field

    def override_table(self, query, query_parameters, dest_table, dry_run=False):
        from google.cloud.bigquery import QueryJobConfig
        from google.cloud.bigquery.job import WriteDisposition

        job_config = QueryJobConfig()
        job_config.query_parameters = query_parameters
        job_config.write_disposition = WriteDisposition.WRITE_TRUNCATE
        job_config.destination = dest_table
        job_config.dry_run = dry_run

        job = self._query_async(query, job_config)

        return BqJob(job)
