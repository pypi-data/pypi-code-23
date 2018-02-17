from abc import ABCMeta, abstractmethod


class FileStoreBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_bucket(self, bucket_name, **kwargs):
        pass

    @abstractmethod
    def delete_bucket(self, bucket_name):
        pass

    @abstractmethod
    def list_files(self, bucket_name, prefix, **kwargs):
        pass

    @abstractmethod
    def download_file(self, bucket_name, key, file_name):
        pass

    @abstractmethod
    def get_object(self, bucket_name, key, **kwargs):
        pass

    @abstractmethod
    def put_object(self, bucket_name, key, obj, **kwargs):
        pass

    @abstractmethod
    def download_fileobj(self, bucket_name, key, file_obj):
        pass

    @abstractmethod
    def upload_file(self, bucket_name, key, file_name):
        pass

    @abstractmethod
    def upload_fileobj(self, bucket_name, key, file_obj):
        pass

    @abstractmethod
    def delete_object(self, bucket_name, key, **kwargs):
        pass
