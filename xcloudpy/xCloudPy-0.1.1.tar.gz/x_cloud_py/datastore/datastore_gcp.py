from x_cloud_py.datastore.datastore_base import DataStoreBase
from google.cloud import datastore

import logging


class GoogleDataStore(DataStoreBase):
    def __init__(self, *args, **kwargs):
        self.client = datastore.Client(project=kwargs.get('project'))

    def delete_table(self, table_name, **kwargs):
        """
        Delete all entities from a certain kind from datastore
        :param table_name:
        :param kwargs:
        :return:
        """
        try:
            query = self.client.query(kind=table_name)
            query.keys_only()
            keys_to_delete = [entity.key for entity in query.fetch()]
            self.client.delete_multi(keys_to_delete)
        except Exception as e:
            logging.exception(
                'Exception in [GoogleDataStore.delete_table] with table_name {} '.format(table_name))
            raise Exception(e)

    def delete_element(self, table_name, key, **kwargs):
        """
        Delete one entity from datastore using kind and key
        :param table_name: String kind of entity
        :param key:  String key of entity
        :param kwargs:
        :return:
        """
        try:
            complete_key = self.client.key(table_name, key)
            self.client.delete(complete_key)
        except Exception as e:
            logging.exception(
                'Exception in [GoogleDataStore.delete_element] with key {} and kind {}'.format(key, table_name))
            raise Exception(e)

    def put_element(self, table_name, item, **kwargs):
        """
        Put one element into Google DataStore
        :param table_name:
        :param item:
        :param kwargs:
        :return:
        """
        complete_key = self.client.key(table_name, kwargs['key'])

        entity = datastore.Entity(key=complete_key)

        entity.update(item)

        self.client.put(entity)

    def create_table(self, table_name, **kwargs):
        raise NotImplementedError("GoogleDataStore does not require to create tables before insert elements")

    def update_throughput(self, table_name, read_capacity_units, write_capacity_units, **kwargs):
        raise NotImplementedError("GoogleDataStore does not have concept of throughput")

    def get_element(self, table_name, key, **kwargs):
        """
        :param table_name:
        :param key:
        :param kwargs:
        :return:
        """
        complete_key = self.client.key(table_name, key)
        return self.client.get(complete_key)
