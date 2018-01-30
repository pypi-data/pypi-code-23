# -*- coding: utf8 -*-
import logging
from collections import OrderedDict

import functools

from ...gcs_utils import gcs_credentials, do_upload, do_delete_all, do_download, s3_moniker, NonRetryException
from ...connection_mixin import ConnectionMixin
from ...dulwich.object_store import BaseObjectStore
from ...dulwich.objects import hex_to_filename, sha_to_hex, Blob


def return_request_result(response, content):
    return response, content


def multi_process_block(f):
    @functools.wraps(f)
    def wrap(_self, *args, **kwargs):
        multi_process_control = _self.get_multi_process_control()
        try:
            result = f(_self, *args, **kwargs)

            multi_process_control.join()

            return result
        except Exception:
            multi_process_control.terminate()
            raise

    return wrap


class GCSObjectStore(ConnectionMixin, BaseObjectStore):
    def __init__(self, connection, use_multiprocess=True, processes=-1):
        super(GCSObjectStore, self).__init__(connection)
        self.__upload_pool = None
        self._use_multiprocess = use_multiprocess
        self._multi_process_control = None
        self._processes = processes
        self._object_store_auth = connection.data_volume_config.object_store_config.get('auth')
        self.__bucket_name = connection.data_volume_config.object_store_config.get('bucket_name')
        self.__volume_id = self._connection.data_volume_config.volume_id
        self._signed_url_service = None

    def delete_all(self, max_files=None):
        return do_delete_all(self.__bucket_name, self.__volume_id, max_files)

    @classmethod
    def get_content_headers(cls, content_type=None):

        headers = OrderedDict()
        if content_type:
            headers['Content-Type'] = content_type

        headers['x-goog-acl'] = 'public-read'
        headers['x-goog-if-generation-match'] = '0'

        return headers

    @property
    def processes(self):
        return self._processes if self.is_multiprocess else 1

    @processes.setter
    def processes(self, value):
        self._processes = value

    @property
    def is_multiprocess(self):
        return self._use_multiprocess and self._processes != 1

    def close(self):
        logging.debug('%s closing', self.__class__)
        if self._multi_process_control is not None:
            self._multi_process_control.close()

        logging.debug('%s closed', self.__class__)

    @classmethod
    def _get_shafile_path(cls, sha):
        # Check from object dir
        return hex_to_filename('objects', sha)

    @classmethod
    def on_upload_error(cls, ex):
        raise ex

    def get_multi_process_control(self):
        self.__init_multi_process_if_needed()
        return self._multi_process_control

    def __init_multi_process_if_needed(self):
        if self._multi_process_control is None:
            from ...multi_process_control import get_multi_process_control

            self._multi_process_control = get_multi_process_control(self.processes)

    def upload(self, obj, head_url=None, put_url=None, callback=None):
        object_name = self._get_shafile_path(obj.sha)

        if self.__bucket_name and not self.__bucket_name.startswith(s3_moniker):
            credentials = gcs_credentials()
        else:
            credentials = None

        content_type = obj.content_type
        headers = GCSObjectStore.get_content_headers(content_type)

        object_name = '%s/%s' % (self.__volume_id, object_name)

        args = (
            self._object_store_auth,
            self.__bucket_name, object_name, obj.full_path, headers, head_url, put_url, credentials)

        self._multi_process_control.execute(do_upload, args=args, callback=callback)

    def add_object(self, obj):

        """Add a single object to this object store.

        :param obj: Object to add
        """
        self.upload(obj)

    def _get_loose_object(self, sha):
        logging.debug('get object %s', sha)
        object_name = '%s/%s' % (self.__volume_id, self._get_shafile_path(sha))

        data = do_download(
            self._object_store_auth, self.__bucket_name, object_name, signed_url_service=self._signed_url_service)

        blob = Blob()
        blob.set_raw_chunks([data], sha)
        return blob

    def get_raw(self, name):
        """Obtain the raw text for an object.

        :param name: sha for the object.
        :return: tuple with numeric type and object contents.
        """
        hex_sha = name

        if len(name) != 40 and len(name) != 20:
            raise AssertionError("Invalid object name %r" % name)

        if hex_sha is None:
            hex_sha = sha_to_hex(name)

        ret = self._get_loose_object(hex_sha)
        if ret is not None:
            return ret.type_num, ret.as_raw_string()

        raise KeyError(hex_sha)

    @property
    def packs(self):
        raise NotImplementedError(self.packs)

    def __iter__(self):
        raise NotImplementedError(self.__iter__)

    @multi_process_block
    def add_objects(self, objects, callback=None):
        for obj in objects:
            self.upload(obj, callback=callback)

    def contains_packed(self, sha):
        raise NotImplementedError(self.contains_packed)

    def contains_loose(self, sha):
        raise NotImplementedError(self.contains_loose)
