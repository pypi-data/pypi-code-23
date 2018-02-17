from x_cloud_py.datastore.datastore_base import DataStoreBase

import boto3
import logging


class DynamoDBDataStore(DataStoreBase):
    """
    """



    def __init__(self, *args, **kwargs):
        self.client = boto3.client('dynamodb',**kwargs)
        self.resource = boto3.resource('dynamodb',**kwargs)

    def put_element(self, table_name, item, **kwargs):
        """
        Insert / Update an item of a DynamoDB table
        :param table_name: DynamoDB table
        :param item: dict
        :return:
        """
        try:
            table = self.resource.Table(table_name)
            response = table.put_item(
                Item=item
            )
            return response
        except Exception as e:
            logging.exception(
                'Exception in [DynamoDBDataSource.put_element] with table_name {} and item {}'.format(table_name, item))
            raise e

    def put_elements(self, table_name, items, **kwargs):
        """
        Put multiple elements in dynamoDB table in batch mode
        :param table_name:
        :param items:
        :param kwargs:
        :return:
        """
        try:
            table = self.resource.Table(table_name)
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
        except Exception as e:
            logging.exception(
                'Exception in [DynamoDBDataSource.put_elements] with table_name {} and item size {}'.format(table_name, str(len(items))))
            raise e


    def get_element(self, table_name, key, **kwargs):
        """
        Returns an item from a DynamoDB table given the table name and key
        :param table_name: DynamoDB table
        :param key: Item key
        """
        try:
            table = self.resource.Table(table_name)
            response = table.get_item(Key=key)
            if 'Item' in response:
                return response['Item']
            else:
                return {}
        except Exception as e:
            logging.exception(
                'Exception in [DynamoDBDataSource.get_item] with key {} and table {}'.format(key, table_name))
            raise e

    def update_throughput(self, table_name, read_capacity_units, write_capacity_units, **kwargs):
        try:
            table = self.resource.Table(table_name)
            response = table.update(
                ProvisionedThroughput={
                    'ReadCapacityUnits': read_capacity_units,
                    'WriteCapacityUnits': write_capacity_units
                }
            )
            waiter = self.client.get_waiter('table_exists')
            waiter.wait(
                TableName=table_name,
                WaiterConfig={
                    'Delay': 20,
                    'MaxAttempts': 10
                }
            )
            return response
        except Exception as e:
            logging.exception(
                'Exception in [DynamoDBDataSource.update_throughput] with table name {}'.format(table_name))
            raise e

    def delete_table(self, table_name, **kwargs):
        """
        Delete dynamoDB table and waits until operation completes
        :param table_name:
        :param kwargs:
        :return:
        """
        try:
            self.resource.Table(table_name).delete()
            waiter = self.client.get_waiter('table_not_exists')
            waiter.wait(
                TableName=table_name,
                WaiterConfig={
                    'Delay': 20,
                    'MaxAttempts': 10
                }
            )
        except Exception as e:
            logging.exception(
                'Exception in [DynamoDBDataSource.delete_table] with table_name {}'.format(table_name))
            raise e

    def delete_element(self, table_name, key, **kwargs):
        """
        Delete element from dynamoDB table
        :param table_name: String table name
        :param key: dict A map of attribute names to AttributeValue objects, representing the primary key of the item to delete.
                    For the primary key, you must provide all of the attributes. For example, with a simple primary key,
                    you only need to provide a value for the partition key. For a composite primary key, you must provide
                    values for both the partition key and the sort key.
        :param kwargs:
        :return:
        """
        try:
            table = self.resource.Table(table_name)
            table.delete_item(Key=key)
        except Exception as e:
            logging.exception(
                'Exception in [DynamoDBDataSource.delete_element] with key {} and table {}'.format(key, table_name))
            raise e

    def create_table(self, table_name, **kwargs):
        """
        Creates a table in DynamoDB and waits until table is created
        :param table_name: String table name
        :param kwargs: should contain required params for create table otherwise default table props are used
        :return: String table name
        """
        default_table_pros = {
            'TableName': table_name,
            'AttributeDefinitions': [{
                'AttributeName': 'id',
                'AttributeType': 'S'
            }],
            'KeySchema': [
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        }
        try:
            table_props = {**default_table_pros, **kwargs}

            result = self.resource.create_table(**table_props)

            waiter = self.client.get_waiter('table_exists')
            waiter.wait(
                TableName=table_name,
                WaiterConfig={
                    'Delay': 20,
                    'MaxAttempts': 10
                }
            )
            return result.table_name
        except Exception as e:
            logging.exception(
                'Exception in [DynamoDBDataSource.create_table] with table_name {} and kwargs {}'.format(table_name,
                                                                                                         kwargs))
            raise e
