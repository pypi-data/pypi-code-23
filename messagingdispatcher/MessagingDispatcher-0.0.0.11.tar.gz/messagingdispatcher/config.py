import os

CONFIG = {
   'relationaldb_host': '',
   'relationaldb_username':'',
   'relationaldb_password':'',
   'relationaldb_dbname':'',
   'elasticsearch_endpoint':'',
   'aws_key_id':os.getenv('AWS_KEY_ID'),
   'aws_secret_key':os.getenv('AWS_SECRET_KEY_ID')}