from x_cloud_py.filestore.filestore_cgp import GoogleCloudStorage
from x_cloud_py.filestore.filestore_aws import S3FileStore


class FileStoreFactory(object):
    def factory(provider,**kwargs):
        if provider == "AWS":
            return S3FileStore(**kwargs)
        if provider == "GCP":
            return GoogleCloudStorage(**kwargs)
        assert 0, "Bad DataStore creation: " + provider

    factory = staticmethod(factory)

