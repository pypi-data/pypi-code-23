"""
Contains application settings.
"""
import os

DEBUG = os.environ.get('DEBUG', False)
API_URL = os.environ.get('BIOBANK_API_URL','http://api.biobank.test')
CLIENT_ID = os.environ.get('BIOBANK_CLIENT_ID', 2)
CLIENT_SECRET = os.environ.get('BIOBANK_CLIENT_SECRET', '5H7P8O9RWxvijIcrdEdStqEt2n6kIW7K6Lb7TJn8')
CLIENT_GRANT = os.environ.get('BIOBANK_CLIENT_GRANT','password')
