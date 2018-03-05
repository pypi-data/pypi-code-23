import io
import os.path
import pathlib
import mimetypes

try:
    import botocore
    import boto3
except ImportError:
    pass

import uuid

import falcon


class Document:
    def __init__(self, name, uid, path, storage_type=None, **kwargs):
        self.name = name
        self.uid = uid
        self.path = path
        self.storage_type = storage_type
        self.details = kwargs


class StorageException(Exception):
    pass


class S3FileStore:
    storage_type = 'OBJECT::S3'

    def __init__(self, bucket, prefix='/', uidgen=uuid.uuid4,
                 default_content_type='application/octet-stream',
                 endpoint=None
                 ):
        if not prefix.startswith('/'):
            raise AssertionError('S3ImageStore requires an absolute path.')

        # Setup the mimetypes database
        mimetypes.init()

        # Remove any trailing slash
        self.prefix = prefix.rstrip('/') if prefix != '/' else prefix
        self.bucket = bucket
        self.uidgen = uidgen
        self.default_content_type = default_content_type
        self.endpoint = endpoint

    @property
    def connection(self):
        return boto3.resource('s3')

    @property
    def client(self):
        return boto3.client('s3', endpoint_url=self.endpoint)

    def make_download_url(self, doc, expires_in=60):
        return self.client.generate_presigned_url(
            ClientMethod='get_object',
            ExpiresIn=expires_in,
            Params={
                'Bucket': self.bucket,
                'Key': doc.path.lstrip('/'),
                'ResponseContentDisposition': 'attachment; filename="{}"'.format(doc.name)
            })

    def make_response(self, doc, resp):
        resp.status = falcon.HTTP_303
        resp.location = self.make_download_url(doc)

    def remove(self, path):
        obj = self.connection.Object(self.bucket, path.lstrip('/'))
        resp = obj.delete()

        if resp['ResponseMetadata']['HTTPStatusCode'] == 204:
            return True
        else:
            return False

    def save(self, filename, fp, path=None):
        unique_name = self.uidgen()
        (content_type, content_encoding) = mimetypes.guess_type(filename)

        if not content_type:
            content_type = self.default_content_type

        name = unique_name

        if path:
            final_path = self.prefix + '/' + path.strip('/') + '/' + str(name)
        else:
            final_path = self.prefix + '/' + str(name)

        final_path = os.path.normpath(final_path)

        if not final_path.startswith(self.prefix):
            raise StorageException('Invalid path')

        # This could raise an exception, catch it at the app level so you have the reporting
        # capabilities... if only python had a Result type...
        obj = self.connection.Object(self.bucket, final_path.lstrip('/'))
        result = obj.put(Body=fp, ContentType=content_type, Metadata={ 'original-filename': filename })

        if ('ResponseMetadata' in result and
            result['ResponseMetadata'].get('HTTPStatusCode', None) in (200, 201)):

            return Document(uid=unique_name, name=filename, path=final_path,
                            storage_type=self.storage_type, response=result)
        else:
            raise StorageException('Unknown State. Response Type Unknown.')


class LocalFileStore:
    storage_type = 'FILE::LOCAL'

    def __init__(self, path, uidgen=uuid.uuid4, default_content_type='application/octet-stream',
                 _fopen=io.open):
        self.path = pathlib.Path(path)
        self.uidgen = uidgen
        self._fopen = _fopen

        # Setup the mimetypes database
        mimetypes.init()
        self.default_content_type = default_content_type

    def remove(self, path):
        try:
            os.remove(path)
        except FileNotFoundError as e:
            return True
        else:
            return True

    def save(self, filename, fp, path=None):
        unique_name = self.uidgen()

        parent = self.path.joinpath(path)

        parent.mkdir(parents=True, exist_ok=True)
        final_path = parent.joinpath(str(unique_name))

        with open(final_path, 'wb') as f:
            result = f.write(fp.read())

        return Document(uid=unique_name,
                        name=filename,
                        path=str(final_path),
                        storage_type=self.storage_type,
                        response=result)

    def make_response(self, doc, resp):
        (content_type, content_encoding) = mimetypes.guess_type(doc.name)

        if not content_type:
            content_type = self.default_content_type

        resp.stream = self._fopen(doc.path, 'rb')
        stream_len = os.path.getsize(doc.path)
        resp.content_length = stream_len

        resp.downloadable_as = doc.name

        resp.content_type = content_type

        resp.status = falcon.HTTP_200
