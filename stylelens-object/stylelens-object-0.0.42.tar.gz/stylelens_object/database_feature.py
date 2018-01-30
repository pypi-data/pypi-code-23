import os
from pymongo import MongoClient


DB_FEATURE_HOST = os.environ['DB_OBJECT_FEATURE_HOST']
DB_FEATURE_PORT = os.environ['DB_OBJECT_FEATURE_PORT']
DB_FEATURE_NAME = os.environ['DB_OBJECT_FEATURE_NAME']
DB_FEATURE_USER = os.environ['DB_OBJECT_FEATURE_USER']
DB_FEATURE_PASSWORD = os.environ['DB_OBJECT_FEATURE_PASSWORD']


class DataBaseFeature(object):
  def __init__(self):
    self.client = MongoClient('mongodb://' + DB_FEATURE_USER + ':' + DB_FEATURE_PASSWORD + '@' + DB_FEATURE_HOST + ':' + DB_FEATURE_PORT)
    self.db = self.client[DB_FEATURE_NAME]


