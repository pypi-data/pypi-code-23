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
    print 'prepare a "secret.py" has aws_id="your AMI id", aws_key="your AMI key"'
    
    exit(0)



try:
    mango = MongoClient(host='dsnotebook.bid', port=27017, username=secret.mongo_user, password=secret.mongo_pwd)

    db=mango['explore']
    coll=db['research']
except:
    mango = MongoClient(host='dsnotebook.bid', port=27017, username='face', password='rekognition')

    db=mango['explore']
    coll=db['research']
    
    print 'no mango'


client = boto3.client(
    'rekognition',
    region_name='us-east-1',
    aws_access_key_id = secret.aws_id,
    aws_secret_access_key=secret.aws_key
)



def face2folder2mango(path):
    #collection={}
    if path[-1]!='/':
        path+='/'
    dr=os.listdir(path)
    
    print len(dr), 'files in the folder'
    flag = raw_input('all many pics do you want to push (blank for all)? ')
    if not flag.strip():
        flag=len(dr)
    
    flag=int(flag)
    if flag>=len(dr):
        flag=len(dr)
    dr=dr[0:flag]
    print 'pushing...', len(dr)
    
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
