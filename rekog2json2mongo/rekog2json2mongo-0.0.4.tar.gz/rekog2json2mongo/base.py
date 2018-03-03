import os
import sys
from time import time, ctime
import boto3
import json
from pymongo import MongoClient


import imp

try:
    secret = imp.load_source('key','secret.py')
except:
    print 'plase create secret.py with boto3, mongodb credentials'
    exit(0)




mango = MongoClient(host='dsnotebook.bid', port=27017, username=secret.mongo_user, password=secret.mongo_pwd)

db=mango['explore']
coll=db['research']


client = boto3.client(
    'rekognition',
    aws_access_key_id = secret.aws_id,
    aws_secret_access_key=secret.aws_key
)



def face2folder2mango(path):
    #collection={}
    dr=os.listdir(path)[:3]
    print len(dr)
    
    n=0
    start=time()
    for i in dr:
        n+=1
        
        try:

            with open(path+i, 'rb') as image:
                response = client.detect_faces(Image={'Bytes': image.read()}, Attributes=['ALL',])
            print n, i,'{:.2f}s'.format(time()-start)
            
        except Exception as e:
            print e
            
        
        #collection['picture_name']=i
        #collection['api_result']=response
        try:
            with open('result.csv', 'a') as fh:
                one={'picture_name':i, 'api_result':response}
                fh.write(json.dumps(one))
                fh.write('\n')
        except Exception as e:
            print e
            
        try:
            coll.insert_one(one)
            start=time()
        except Exception as e:
            print e
            
    print 'done'
    #return collection
