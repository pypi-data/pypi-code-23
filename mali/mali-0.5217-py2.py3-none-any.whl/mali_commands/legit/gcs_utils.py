# -*- coding: utf8 -*-
import logging
import requests
import six
from requests import HTTPError
from .path_utils import remove_moniker


class GCSServiceOperationError(Exception):
    pass


__gcs_service = None
__gcs_credentials = None


class closing_with_condition(object):
    def __init__(self, thing, should_close):
        self.thing = thing
        self.should_close = should_close

    def __enter__(self):
        return self.thing

    def __exit__(self, *exc_info):
        if self.should_close:
            self.thing.close()


def gcs_credentials():
    import google.auth.exceptions

    global __gcs_credentials

    if __gcs_credentials is None:
        try:
            __gcs_credentials, _ = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            pass

    return __gcs_credentials


def gcs_service(credentials=None):
    from google.cloud import storage

    global __gcs_service

    if __gcs_service is None:
        __gcs_service = storage.Client(credentials=credentials)

    return __gcs_service


class GCSService(object):
    RETRYABLE_ERRORS = (IOError, )
    DEFAULT_MIMETYPE = 'application/octet-stream'
    NUM_RETRIES = 5

    def __init__(self, signed_url_service):
        self.signed_url_service = signed_url_service


class GCSDownload(GCSService):
    def __init__(self, auth_method, signed_url_service):
        super(GCSDownload, self).__init__(signed_url_service)
        self._auth_method = auth_method

    def download(self, object_name):
        auth_session = get_auth_session(self._auth_method)

        signed_urls = self.signed_url_service.get_signed_urls(['GET'], [object_name])
        url = signed_urls['GET'][0]

        r = auth_session.get(url)
        r.raise_for_status()
        data = r.content

        logging.debug('downloaded  %s(%s)', object_name, len(data))

        return data


class GCSDownloadDirectDownload(GCSService):
    def __init__(self):
        super(GCSDownloadDirectDownload, self).__init__(None)

    @classmethod
    def download(cls, bucket_name, object_name):
        gcs = gcs_service()

        blob = gcs.bucket(bucket_name).blob(object_name)
        data = blob.download_as_string()

        return data


class S3DownloadDirectDownload(GCSService):
    def __init__(self):
        super(S3DownloadDirectDownload, self).__init__(None)

    @classmethod
    def download(cls, bucket_name, object_name):
        import boto3

        s3 = boto3.resource('s3')

        obj = s3.Object(bucket_name, object_name)
        try:
            return obj.get()['Body'].read()
        except Exception as ex:
            return None


class GCSUploadDirect(GCSService):
    def __init__(self):
        super(GCSUploadDirect, self).__init__(None)

    @classmethod
    def upload(cls, bucket_name, object_name, file_obj, headers, credentials=None):
        from google.api_core.exceptions import NotFound, PermissionDenied

        gcs = gcs_service(credentials=credentials)

        blob = gcs.bucket(bucket_name).blob(object_name)

        content_type = headers.get('Content-Type')

        try:
            blob.upload_from_file(file_obj, content_type)
        except NotFound:
            raise NonRetryException('bucket %s not found' % bucket_name)
        except PermissionDenied:
            raise NonRetryException('access denied to bucket %s' % bucket_name)


class S3UploadDirect(GCSService):
    def __init__(self):
        super(S3UploadDirect, self).__init__(None)

    @classmethod
    def upload(cls, bucket_name, object_name, file_obj, headers, credentials=None):
        import boto3

        s3 = boto3.client('s3')
        try:
            s3.upload_fileobj(file_obj, bucket_name, object_name)
        except s3.exceptions.NoSuchBucket:
            raise NonRetryException('No such S3 Bucket %s' % bucket_name)

    @classmethod
    def copy(cls, src, dest):
        import boto3
        from botocore.exceptions import ClientError

        s3 = boto3.client('s3')
        try:
            bucket_name, key = dest.split('/', 1)
            s3.copy_object(Bucket=bucket_name, CopySource=src, Key=key)
        except s3.exceptions.NoSuchBucket:
            raise NonRetryException('No such S3 Bucket %s' % bucket_name)
        except ClientError as ex:
            if ex.response.get('Error', {}).get('Code') == 'AccessDenied':
                raise NonRetryException('Access Denied when copying %s' % src)

            raise


class FileWithCallback(object):
    def __init__(self, file_obj, callback):
        file_obj.seek(0, 2)
        self._total = file_obj.tell()
        file_obj.seek(0)

        self._callback = callback
        self._file_obj = file_obj

    def __len__(self):
        return self._total

    def read(self, size):
        data = self._file_obj.read(size)

        if six.PY3 and isinstance(data, six.string_types):
            data = data.encode()

        if self._callback is not None:
            self._callback(len(data))

        return data


class GCSUpload(GCSService):
    def __init__(self, auth_method, head_url, put_url):
        super(GCSUpload, self).__init__(None)
        self._head_url = head_url
        self._put_url = put_url
        self._auth_method = auth_method

    def upload(self, file_obj, headers, callback=None):
        auth_session = get_auth_session(self._auth_method)

        resp = None

        file_obj_with_callback = FileWithCallback(file_obj, callback)

        if self._head_url:
            resp = auth_session.head(self._head_url)

            if resp.status_code in (204, 404):
                logging.debug('file not found, uploading')
                resp = None

        if resp is None:
            resp = auth_session.put(self._put_url, data=file_obj_with_callback, headers=headers)

        if resp.status_code in (401, 403):
            raise NonRetryException()

        resp.raise_for_status()


class GCSDeleteAll(GCSService):
    @classmethod
    def delete_all(cls, bucket_name, volume_id, max_files=None):
        import google.cloud.exceptions

        logging.info('delete all at %s/%s', bucket_name, volume_id)
        gcs = gcs_service()

        try:
            list_iter = gcs.bucket(bucket_name).list_blobs(prefix=volume_id)
        except google.cloud.exceptions.NotFound:
            logging.warning('bucket %s was not found', bucket_name)
            return

        total_deleted = 0
        for blob in list_iter:
            try:
                gcs.bucket(bucket_name).delete_blob(blob.name)
            except google.cloud.exceptions.NotFound:
                pass

            total_deleted += 1

            if max_files is not None and max_files == total_deleted:
                break

        logging .info('total deleted %s', total_deleted)

        return total_deleted


def get_auth_session(auth_method):
    if auth_method == 'gcloud':
        import google.auth.transport.requests

        credentials = gcs_credentials()

        return google.auth.transport.requests.AuthorizedSession(credentials)

    return requests


s3_moniker = 's3://'


class NonRetryException(Exception):
    pass


def __retry_if_retry_possible_error(exception):
    logging.debug('got retry exception (upload/download) %s', exception)

    return not isinstance(exception, NonRetryException)


def _default_retry():
    from retrying import retry

    def decor(f):
        return retry(retry_on_exception=__retry_if_retry_possible_error, wait_exponential_multiplier=50, wait_exponential_max=5000)(f)

    return decor


def do_upload(auth, bucket_name, object_name, full_path_to_data, headers, head_url, put_url, credentials=None, callback=None):
    global __gcs_credentials

    if credentials is not None:
        __gcs_credentials = credentials

    def handle_file_object():
        if hasattr(full_path_to_data, 'read'):
            full_path_to_data.seek(0)
            return full_path_to_data

        return open(full_path_to_data, 'rb')

    @_default_retry()
    def with_retry_to_s3():
        file_obj = handle_file_object()

        S3UploadDirect().upload(bucket_name, object_name, file_obj, headers)

    @_default_retry()
    def with_retry_transfer_s3():
        full_s3_path = remove_moniker(full_path_to_data)
        object_name_with_bucket = bucket_name + '/' + object_name
        S3UploadDirect().copy(full_s3_path, object_name_with_bucket)

    @_default_retry()
    def with_retry_to_gcs():
        file_obj = handle_file_object()

        try:
            if put_url:
                GCSUpload(auth, head_url, put_url).upload(file_obj, headers, callback)
                return

            GCSUploadDirect().upload(bucket_name, object_name, file_obj, headers)
        except HTTPError as e:
            if e.response.status_code != 412:  # precondition
                pass
            else:
                raise

    upload_method = with_retry_to_gcs

    if bucket_name is not None and bucket_name.startswith(s3_moniker):
        if full_path_to_data.startswith(s3_moniker):
            upload_method = with_retry_transfer_s3
        else:
            upload_method = with_retry_to_s3

    if bucket_name is not None:
        bucket_name = remove_moniker(bucket_name)

    upload_method()


def do_download(auth, bucket_name, object_name, signed_url_service=None):
    @_default_retry()
    def with_retry_s3():
        return S3DownloadDirectDownload().download(bucket_name, object_name)

    if bucket_name is not None:
        if bucket_name.startswith(s3_moniker):
            bucket_name = remove_moniker(bucket_name)
            return with_retry_s3()

        bucket_name = remove_moniker(bucket_name)

    @_default_retry()
    def with_retry():
        if signed_url_service:
            return GCSDownload(auth, signed_url_service).download(object_name)

        return GCSDownloadDirectDownload().download(bucket_name, object_name)

    return with_retry()


def do_delete_all(bucket_name, volume_id, max_files):
    return GCSDeleteAll(signed_url_service=None).delete_all(bucket_name, volume_id, max_files)
