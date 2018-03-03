import os
import sys
from time import time, ctime

import imp

try:
    secret = imp.load_source('key','secret.py')
except:
    print 'plase create secret.py with boto3, mongodb credentials'
    exit(0)

print secret
print secret.key
print secret.mongo_user

def face2folder2mango():
    pass
