import pytest
import os

from pymongal.database_mongo import MongoDatabase

test_db_name = 'TESTING_DB'

if os.environ.get('DATABASE_HOST') and os.environ.get('DATABASE_PORT'):
    @pytest.fixture(autouse=True)
    def db():
        database = MongoDatabase(os.environ.get('DATABASE_HOST'), os.environ.get('DATABASE_PORT'), test_db_name)
        raw_db = database.get_pymongo()
        project1_mongo = project1.copy()
        project1_mongo['_id'] = project1_mongo['id']
        project2_mongo = project2.copy()
        project2_mongo['_id'] = project2_mongo['id']
        raw_db.project.insert(project1_mongo)
        raw_db.project.insert(project2_mongo)
        yield database
        raw_db.client.drop_database(test_db_name)


    from tests.common_tests import *
