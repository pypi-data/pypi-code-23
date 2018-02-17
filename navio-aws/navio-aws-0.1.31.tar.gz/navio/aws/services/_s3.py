import boto3
import botocore
import os
import uuid
import fnmatch
import re
import sh
import mimetypes
import copy
import traceback
import sys
from boto3.s3.transfer import S3Transfer
from navio.aws.services._session import AWSSession
from concurrent import futures

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


class AWSS3(AWSSession):

    def __init__(self, **kwargs):
        super(
            self.__class__,
            self
        ).__init__(kwargs['profile_name'])

    def bucket_exists(self, **kwargs):
        if 'bucket_name' not in kwargs:
            raise Exception('Argument missing: bucket_name')

        s3api = self.session.client('s3')

        try:
            s3api.head_bucket(Bucket=kwargs.get('bucket_name'))
        except botocore.exceptions.ClientError as err:
            err_msg = err.response['Error']['Message']
            err_code = err.response['Error']['Code']
            if (err_msg != ("An error occurred (403) when calling "
                            "the HeadBucket operation: Forbidden")):
                return False
            else:
                raise Exception("Error calling head_bucket: {}".format(
                    err_msg), sys.exc_info()[2])

        return True

    def sync(self, **kwargs):
        if 'metadata' in kwargs:
            return self._sync_with_metadata(**kwargs)
        else:
            return self._sync_no_metadata(**kwargs)

    def _sync_with_metadata(self, **kwargs):
        s3api = self.session.client('s3')
        s3res = self.session.resource('s3')

        result = dict()
        result['updated_files'] = list()

        s3_bucket, s3_key = self._split_s3_url(kwargs['destination'])
        s3_files_list = self._list_s3_files(s3_bucket, s3_key)

        with sh.pushd(kwargs['source']):
            files = list()
            for root, dirnames, filenames in os.walk('.'):
                for filename in filenames:
                    files.append(os.path.join(root, filename))

            files_to_remove = [
                x for x in s3_files_list if './{}'.format(x) not in files]

            result['updated_files'].extend(files_to_remove)

            for key in files_to_remove:
                s3_key_full = '{}{}'.format(s3_key, key)
                futures_results = dict()
                with futures.ThreadPoolExecutor(max_workers=4) as executor:
                    futures_results[executor.submit(self._delete_file, s3api, {
                        's3_bucket': s3_bucket,
                        's3_key': s3_key_full
                    })] = filename

                for future in futures.as_completed(futures_results):
                    if future.exception() is not None:
                        print(
                            'Error/Warning: file={}, error={}'.format(
                                futures_results[future],
                                future.exception()
                            )
                        )

            for filename in files:
                content_type, content_encoding = self._get_content_type(
                    filename)
                metadata_full_obj = copy.deepcopy(
                    self._get_metadata_for_file(filename, kwargs['metadata']))
                http_metadata = dict()

                result['updated_files'].append(filename[1:])

                # print('gmeta:{}'.format(metadata_full_obj))

                if 'Cache-Control' in metadata_full_obj['metadata']:
                    http_metadata['Cache-Control'] =\
                        metadata_full_obj['metadata'].pop(
                        'Cache-Control', None)

                if 'Content-Type' in metadata_full_obj['metadata']:
                    http_metadata['Content-Type'] =\
                        metadata_full_obj['metadata'].pop(
                        'Content-Type', None)
                elif content_type:
                    http_metadata['Content-Type'] = content_type

                if 'Content-Encoding' in metadata_full_obj['metadata']:
                    http_metadata['Content-Encoding'] =\
                        metadata_full_obj['metadata'].pop(
                            'Content-Encoding', None)
                elif content_encoding:
                    http_metadata['Content-Encoding'] = content_encoding

                s3_key_full = '{}{}'.format(s3_key, filename[2:])
                futures_results = dict()
                with futures.ThreadPoolExecutor(max_workers=4) as executor:
                    futures_results[executor.submit(self._upload_file, s3api, {
                        'filename': filename,
                        's3_bucket': s3_bucket,
                        's3_key': s3_key_full,
                        'acl': kwargs['acl'],
                        'pattern': metadata_full_obj['pattern'],
                        'metadata': metadata_full_obj['metadata'],
                        'http-metadata': http_metadata
                    })] = filename

                for future in futures.as_completed(futures_results):
                    if future.exception() is not None:
                        print('Error/Warning: file={}, error={}'.format(
                            futures_results[future],
                            future.exception()
                        )
                        )

        return result

    def _delete_file(self, s3api, params):
        try:
            print('Removing: s3://{}/{}'.format(
                params['s3_bucket'],
                params['s3_key']
            )
            )
            s3api.delete_object(
                Bucket=params['s3_bucket'],
                Key=params['s3_key'],
            )
        except Exception as e:
            print("Warning: file {} delete error: ({}){}".format(
                params['filename'], type(e), str(e)))

    def _upload_file(self, s3api, metadata):
        with open(metadata['filename'], 'rb') as file:
            print(
                'Uploading: {pattern} {filename} ->'
                ' s3://{bucket}/{key}'.format(
                    pattern=metadata['pattern'],
                    filename=metadata['filename'],
                    bucket=metadata['s3_bucket'],
                    key=metadata['s3_key']
                )
            )
            try:
                if 'Cache-Control' in metadata['http-metadata']:
                    s3api.put_object(
                        Body=file,
                        Bucket=metadata['s3_bucket'],
                        Key=metadata['s3_key'],
                        ACL=metadata['acl'],
                        Metadata=metadata['metadata'],
                        ContentType=metadata['http-metadata']
                        .get('Content-Type', 'application/octet-stream'),
                        ContentLength=os.path.getsize(metadata['filename']),
                        CacheControl=metadata['http-metadata']
                        .get('Cache-Control'),
                    )
                else:
                    s3api.put_object(
                        Body=file,
                        Bucket=metadata['s3_bucket'],
                        Key=metadata['s3_key'],
                        ACL=metadata['acl'],
                        Metadata=metadata['metadata'],
                        ContentType=metadata['http-metadata']
                        .get('Content-Type', 'application/octet-stream'),
                        ContentLength=os.path.getsize(metadata['filename'])
                    )
            except Exception as e:
                print("Warning: file {} copy error: ({}){}".format(
                    metadata['filename'], type(e), str(e)))
                traceback.print_exc(file=sys.stderr)

    def _get_metadata_for_file(self, filename, metadatas):
        for metadata in metadatas:
            if metadata.get('pattern') == '.*':
                default_metadata = metadata['metadata']

            if type(metadata.get('pattern')) == str:
                metadata['pattern'] = [metadata['pattern']]

            for pattern in metadata['pattern']:
                if re.search(pattern, filename):
                    return metadata

    def _list_s3_files(self, s3_bucket, s3_key):
        result = list()

        s3api = self.session.client('s3')
        paginator = s3api.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=s3_bucket, Prefix=s3_key)
        for page in page_iterator:
            if "Contents" in page:
                for key in page["Contents"]:
                    result.append(key['Key'])

        return result

    def _split_s3_url(self, s3_url):
        url = urlparse(s3_url)
        s3_bucket = url.netloc
        s3_key = url.path

        if s3_key.endswith('/'):
            s3_key = "%s%s" % (s3_key, s3_url)

        if s3_key.startswith('/'):
            s3_key = s3_key[1:]

        return (s3_bucket, s3_key)

    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)
