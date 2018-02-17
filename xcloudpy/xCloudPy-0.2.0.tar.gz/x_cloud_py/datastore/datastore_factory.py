from x_cloud_py.datastore.datastore_aws import DynamoDBDataStore
from x_cloud_py.datastore.datastore_gcp import GoogleDataStore


class DataStoreFactory(object):
    def factory(provider,**kwargs):
        if provider == "AWS":
            return DynamoDBDataStore(**kwargs)
        if provider == "GCP":
            return GoogleDataStore(**kwargs)
        assert 0, "Bad DataStore creation: " + provider

    factory = staticmethod(factory)

