from x_cloud_py.filestore.filestore_base import FileStoreBase

import logging
from google.cloud.storage.client import Client


class GoogleCloudStorage(FileStoreBase):
    def __init__(self, *args, **kwargs):
        self.client = Client(**kwargs)

    def create_bucket(self, bucket_name, **kwargs):
        try:
            basic_request = {
                'bucket_name': bucket_name
            }
            create_bucket_request = {**basic_request, **kwargs}
            self.client.create_bucket(**create_bucket_request)
        except Exception as e:
            logging.exception(
                'Exception in [GoogleCloudStorage.create_bucket] with bucket_name {} and kwargs {}'.format(bucket_name,
                                                                                                           kwargs))
            raise e
