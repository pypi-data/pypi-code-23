import os
from pymongo import MongoClient


DB_HOST = os.environ['DB_IMAGE_HOST']
DB_PORT = os.environ['DB_IMAGE_PORT']
DB_NAME = os.environ['DB_IMAGE_NAME']
DB_USER = os.environ['DB_IMAGE_USER']
DB_PASSWORD = os.environ['DB_IMAGE_PASSWORD']


class DataBase(object):
  def __init__(self):
    self.client = MongoClient('mongodb://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + ':' + DB_PORT)
    self.db = self.client[DB_NAME]


