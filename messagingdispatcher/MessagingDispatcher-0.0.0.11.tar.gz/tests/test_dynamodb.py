import os, sys, unittest
from boto3 import resource
from botocore.exceptions import ClientError
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')
from messagingdispatcher.db.basedb import DBModelMixin
from messagingdispatcher.db.dynamodb import DynamoDB


class TestDynamoDB(unittest.TestCase):
    """ Test Class for DynamoDB """
    def setUp(self):
        self.table_name = 'message-dispatcher-test'
        self.table = resource('dynamodb').Table(self.table_name)

    def create_db_model_mixin(self, primary_id, name):        
        db_model = DBModelMixin()
        db_model.id = primary_id
        db_model.display_name = name
        return db_model

    def assert_model_matches_database_record(self, model, database_record):
        # Assert that the Attributes matches
        self.assertEqual(model.to_dict().keys(), database_record.keys())

        # Assert that the Attribute Values matches
        for key in model.__dict__:
            self.assertEqual(getattr(model, key), database_record.get(key))

    def test_add_success(self):
        # Create item to persist
        db_model = self.create_db_model_mixin(1, "Dark Mocha")

        # Create DynamoDB Object and add data
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        dynamodb.add(db_model)

        # Query the recently added Item and check if it matches
        response = self.table.get_item(Key={"id": db_model.id}).get("Item")
        self.assert_model_matches_database_record(db_model, response)

        # Clear data for test function
        self.table.delete_item(Key={"id": db_model.id})

    def test_add_throws_type_error(self):
        # Create DynamoDB Object and add DBModelMixin as the expected type
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        with self.assertRaises(TypeError):
            # Add a list which is not the expected type
            dynamodb.add([1, 2, 3])

    def test_add_batch_throws_type_error_on_non_list_items(self):
        # Create DynamoDB Object
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        with self.assertRaises(TypeError):
            # Add a String which is not the expected type in add_batch
            dynamodb.add_batch("STRING")

    def test_add_batch_throws_type_error_on_items_contain_invalid_type(self):
        # Create item to persist
        db_model = self.create_db_model_mixin(1, "Chocolate Mocha")

        # Create DynamoDB Object
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        with self.assertRaises(TypeError):
            # Add a String which is not the expected type in add_batch
            dynamodb.add_batch([db_model, {1, 34}])

    def test_add_batch_success(self):
        # Create item to persist
        db_model1 = self.create_db_model_mixin(1, "Strawberry Mocha")
        db_model2 = self.create_db_model_mixin(2, "Spearmint Mocha")

        # Create DynamoDB Object and add items
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        self.assertTrue(dynamodb.add_batch([db_model1, db_model2]))

        # Query the recently added Item and check if it matches
        response = self.table.get_item(Key={"id": db_model1.id}).get("Item")
        self.assert_model_matches_database_record(db_model1, response)

        # Query the recently added Item and check if it matches
        response = self.table.get_item(Key={"id": db_model2.id}).get("Item")
        self.assert_model_matches_database_record(db_model2, response)

        # Clear data for test function
        self.table.delete_item(Key={"id": db_model1.id})
        self.table.delete_item(Key={"id": db_model2.id})

    def test_add_batch_throw_client_error(self):
        # Create item to persist
        db_model = self.create_db_model_mixin(1, "Ice Mocha")

        # Create DynamoDB Object and add items
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        with self.assertRaises(ClientError):
            dynamodb.add_batch([db_model, db_model])

    def test_get_returns_existing_record(self):
        # Create item and persist
        db_model = self.create_db_model_mixin(1, "Durian Mocha")
        self.table.put_item(Item=db_model.__dict__)

        # Create DynamoDB Object and get data
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        response = dynamodb.get("id", db_model.id)

        self.assert_model_matches_database_record(db_model, response)

        # Clear data for test function
        self.table.delete_item(Key={"id": db_model.id})

    def test_get_throws_client_error(self):
        # Create item and persist
        db_model = self.create_db_model_mixin(1, "Durian Mocha")
        self.table.put_item(Item=db_model.__dict__)

        # Create DynamoDB Object and get data
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        with self.assertRaises(ClientError):
            dynamodb.get("id", "RANDOMSTRING")

    def test_get_all_success(self):
        # Create item to persist
        db_model1 = self.create_db_model_mixin(1, "Strawberry Mocha")
        self.table.put_item(Item=db_model1.__dict__)

        db_model2 = self.create_db_model_mixin(2, "Spearmint Mocha")
        self.table.put_item(Item=db_model2.__dict__)

        # Create DynamoDB Object and get data
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        response = dynamodb.get_all()

        self.assertEqual(2, len(response))
        self.assert_model_matches_database_record(db_model1, response[1])
        self.assert_model_matches_database_record(db_model2, response[0])

        # Clear data for test function
        self.table.delete_item(Key={"id": db_model1.id})
        self.table.delete_item(Key={"id": db_model2.id})

    def test_update_success(self):
        # Create item and persist
        db_model = self.create_db_model_mixin(1, "Char Siew Mocha")
        self.table.put_item(Item=db_model.__dict__)

        # Initialize new name
        new_name = "Chicken Name"

        # Ensure that database record does not match the new name
        response = self.table.get_item(Key={"id": db_model.id}).get("Item")
        self.assertNotEqual(new_name, response.get("display_name"))

        # Create DynamoDB Object and get data
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        response = dynamodb.update(key="id", value=db_model.id, update_key="display_name", update_value=new_name)

        # Ensure that database record does not match the new name
        response = self.table.get_item(Key={"id": db_model.id}).get("Item")
        self.assertEqual(new_name, response.get("display_name"))

        # Clear data for test function
        self.table.delete_item(Key={"id": db_model.id})

    def test_update_throw_key_error(self):
        # Create item and persist
        db_model = self.create_db_model_mixin(3, "Char Siew Mocha")
        self.table.put_item(Item=db_model.__dict__)

        new_name = 'Spicy Mocha'

        # Create DynamoDB Object and update data with invalid key value pair
        dynamodb = DynamoDB(self.table_name, DBModelMixin)

        with self.assertRaises(KeyError):
            dynamodb.update(key="id", value=234, update_key="display_name", update_value=new_name)

        # Clear data for test function
        self.table.delete_item(Key={"id": db_model.id})

    def test_update_throw_client_error(self):
        # Create item and persist
        db_model = self.create_db_model_mixin(3, "Char Siew Mocha")
        self.table.put_item(Item=db_model.__dict__)

        new_name = 'Spicy Mocha'

        # Create DynamoDB Object and update data with invalid value type
        dynamodb = DynamoDB(self.table_name, DBModelMixin)

        with self.assertRaises(ClientError):
            dynamodb.update(key="id",
                            value="234",
                            update_key="display_name",
                            update_value=new_name)

        # Clear data for test function
        self.table.delete_item(Key={"id": db_model.id})

    def test_delete_success(self):
        # Create item and persist
        db_model = self.create_db_model_mixin(13, "Plum Mocha")
        self.table.put_item(Item=db_model.__dict__)

        # Ensure that the data exists in the table
        response = self.table.get_item(Key={"id": db_model.id}).get("Item")
        self.assertIsNotNone(response)

        # Create DynamoDB Object and delete data
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        dynamodb.delete(key="id", value=db_model.id)

        # Ensure that the data no longer exists in the table
        response = self.table.get_item(Key={"id": db_model.id}).get("Item")
        self.assertIsNone(response)

    def test_delete_throw_key_error(self):
        # Create DynamoDB Object and delete data with non existent key value pair
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        with self.assertRaises(KeyError):
            dynamodb.delete(key="id", value=21342323233)
    
    def test_delete_throw_client_error(self):
        # Create DynamoDB Object and delete data with invalid key
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        with self.assertRaises(ClientError):
            dynamodb.delete(key="sid", value=21342323233)

    def test_purge_success(self):
        # Create item and persist
        db_model = self.create_db_model_mixin(13, "Plum Mocha")
        self.table.put_item(Item=db_model.__dict__)

        # Create DynamoDB Object and purge data
        dynamodb = DynamoDB(self.table_name, DBModelMixin)
        dynamodb.purge()

        response = self.table.scan()
        self.assertEqual(0, response.get('Count'))

    def test_purge_throw_exception(self):
        # Create item and persist
        db_model = self.create_db_model_mixin(13, "Plum Mocha")
        self.table.put_item(Item=db_model.__dict__)

        # Create DynamoDB Object and purge data in an invalid table
        dynamodb = DynamoDB('RANDOMSTRING', DBModelMixin)
        with self.assertRaises(Exception):
            dynamodb.purge()

if __name__ == '__main__':
    unittest.main()