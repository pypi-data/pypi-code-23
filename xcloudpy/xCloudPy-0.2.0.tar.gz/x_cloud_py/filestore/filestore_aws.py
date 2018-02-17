from x_cloud_py.filestore.filestore_base import FileStoreBase

import boto3
import logging


class S3FileStore(FileStoreBase):
    """
    """

    def __init__(self, *args, **kwargs):
        self.client = boto3.client('s3', **kwargs)
        self.resource = boto3.resource('s3', **kwargs)

    def delete_object(self, bucket_name, key, **kwargs):
        """
        Delete object from S3 with specified bucket and key
        :param bucket_name:
        :param key:
        :param kwargs:
        :return:
        """
        try:
            basic_request = {
                'Bucket': bucket_name,
                'Key': key
            }
            delete_object_request = {**basic_request, **kwargs}
            self.client.delete_object(**delete_object_request)
        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.delete_object] with bucket_name {} , key {} and kwargs {}'.format(
                    bucket_name,
                    key,
                    kwargs))
            raise e

    def upload_fileobj(self, bucket_name, key, file_obj):
        """
        Upload specified file to S3
        :param bucket_name:
        :param key:
        :param file_obj:
        :return:
        """
        try:
            self.client.upload_fileobj(file_obj, bucket_name, key)
        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.upload_fileobj] with bucket_name {} , key {} and file_obj {}'.format(
                    bucket_name,
                    key,
                    file_obj))
            raise e

    def download_fileobj(self, bucket_name, key, file_obj):
        """
        Download object from S3 to specified file
        :param bucket_name:
        :param key:
        :param file_obj:
        :return:
        """
        try:
            self.client.download_fileobj(bucket_name, key, file_obj)
        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.download_fileobj] with bucket_name {} , key {} and file_obj {}'.format(
                    bucket_name,
                    key,
                    file_obj))
            raise e

    def put_object(self, bucket_name, key, obj, **kwargs):
        """
        Upload object to S3 to specified bucket and key
        :param bucket_name: String
        :param key: String
        :param obj: b'bytes'|file
        :param kwargs:
        """
        try:
            basic_request = {
                'Bucket': bucket_name,
                'Key': key,
                'Body': obj
            }
            put_object_request = {**basic_request, **kwargs}
            self.client.put_object(**put_object_request)

        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.put_object] with bucket_name {} , key {} and kwargs {}'.format(bucket_name,
                                                                                                          key,
                                                                                                          kwargs))
            raise e

    def get_object(self, bucket_name, key, **kwargs):
        """
        Return object from bucket with bucket_name and key if exists
        :param bucket_name: String bucket name
        :param key: String object key
        :param kwargs:
        :return: StreamingBody object data
        """
        try:
            basic_request = {
                'Bucket': bucket_name,
                'Key': key
            }
            get_object_request = {**basic_request, **kwargs}
            response = self.client.get_object(**get_object_request)
            if 'Body' in response:
                return response['Body']
            else:
                return {}
        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.get_object] with bucket_name {} , key {} and kwargs {}'.format(bucket_name,
                                                                                                          key,
                                                                                                          kwargs))
            raise e

    def download_file(self, bucket_name, key, file_name):
        """
        Download file if exists form specified bucket and key to local file_name
        :param bucket_name:
        :param key:
        :param file_name:
        """
        try:
            self.resource.meta.client.download_file(bucket_name, key, file_name)

        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.download_file] with bucket_name {} , key {} and file_name {}'.format(
                    bucket_name,
                    key,
                    file_name))
            raise e

    def list_files(self, bucket_name, prefix, **kwargs):
        """
        List files from specified bucket and prefix
        :param bucket_name:
        :param prefix:
        :param kwargs:
        :return: list of keys
        """
        try:
            basic_request = {
                'Bucket': bucket_name,
                'Prefix': prefix
            }
            list_files_request = {**basic_request, **kwargs}
            response = self.client.list_objects(**list_files_request)
            if 'Contents' in response:
                response_elements = response['Contents']
                while response['IsTruncated']:
                    if 'NextMarker' in response:
                        request = {**list_files_request, **{'Marker': response['NextMarker']}}
                    else:
                        request = {**list_files_request, **{'Marker': response_elements[-1]['Key']}}
                    response = self.client.list_objects(**request)
                    response_elements.append(response['Contents'])
                return [x['Key'] for x in response_elements]
            else:
                return list()
        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.list_files] with bucket_name {} , prefix {} and kwargs {}'.format(
                    bucket_name,
                    prefix,
                    kwargs))
            raise e

    def upload_file(self, bucket_name, key, file_name):
        self.resource.meta.client.upload_file(file_name, bucket_name, key)

    def delete_bucket(self, bucket_name):
        try:
            self.client.delete_bucket(
                Bucket=bucket_name
            )
        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.delete_bucket] with bucket_name {}'.format(bucket_name))
            raise e

    def create_bucket(self, bucket_name, **kwargs):
        try:
            name_request = {
                'Bucket': bucket_name
            }
            create_bucket_request = {**name_request, **kwargs}
            response = self.client.create_bucket(**create_bucket_request)
            waiter = self.client.get_waiter('bucket_exists')
            waiter.wait(
                Bucket=bucket_name,
                WaiterConfig={
                    'Delay': 123,
                    'MaxAttempts': 123
                }
            )
            return response
        except Exception as e:
            logging.exception(
                'Exception in [S3FileStore.create_bucket] with bucket_name {} and kwargs {}'.format(bucket_name,
                                                                                                    kwargs))
            raise e
