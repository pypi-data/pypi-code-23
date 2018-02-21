from x_cloud_py.datastore.datastore_base import DataStoreBase
from google.cloud import datastore

import logging


class GoogleDataStore(DataStoreBase):
    def __init__(self, *args, **kwargs):
        self.client = datastore.Client(**kwargs)

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
            item_chunks = GoogleDataStore.__chunks(keys_to_delete, 500)
            for chunk in item_chunks:
                with self.client.batch() as batch:
                    for item in chunk:
                        batch.delete(item)
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
        key_field = kwargs.get('key_field', 'key')
        complete_key = self.client.key(table_name, item[key_field])

        entity = datastore.Entity(key=complete_key)
        entity.update(item)
        entity.pop(key_field, None)

        self.client.put(entity)

    def put_elements(self, table_name, items, **kwargs):
        """
        Put multiple entities in a Google Datastore Table
        :param table_name:
        :param items:
        :param kwargs:
        :return:
        """
        try:
            key_field = kwargs.get('key_field', 'key')
            item_chunks = GoogleDataStore.__chunks(items, 500)
            for chunk in item_chunks:
                with self.client.batch() as batch:
                    for item in chunk:
                        complete_key = self.client.key(table_name, item[key_field])

                        entity = datastore.Entity(key=complete_key)
                        entity.update(item)
                        entity.pop(key_field, None)
                        batch.put(entity)


        except Exception as e:
            logging.exception(
                'Exception in [GoogleDataStore.put_elements] with table_name {}'.format(table_name))
            raise e

    def create_table(self, table_name, **kwargs):
        raise NotImplementedError("GoogleDataStore does not require to create tables before insert elements")

    def update_throughput(self, table_name, read_capacity_units, write_capacity_units, **kwargs):
        raise NotImplementedError("GoogleDataStore does not have concept of throughput")

    @staticmethod
    def __chunks(chunkable, n):
        """ Yield successive n-sized chunks from l.
        """
        for i in range(0, len(chunkable), n):
            yield chunkable[i:i + n]

    def get_element(self, table_name, key, **kwargs):
        """
        :param table_name:
        :param key:
        :param kwargs:
        :return:
        """
        try:
            key_field = kwargs.get('key_field', 'key')
            complete_key = self.client.key(table_name, key)

            entity = self.client.get(complete_key)

            item = dict(entity.items())
            item[key_field] = entity.key.id_or_name

            return item

        except Exception as e:
            logging.exception(
                'Exception in [GoogleDataStore.get_element] with table_name {} and key {}'.format(table_name, key))
            raise Exception(e)
