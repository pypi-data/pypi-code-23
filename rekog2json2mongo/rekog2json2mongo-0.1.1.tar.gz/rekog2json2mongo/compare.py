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


client = boto3.client(
    'rekognition',
    region_name='us-east-1',
    aws_access_key_id = secret.aws_id,
    aws_secret_access_key=secret.aws_key
)
    
    
try:

    mango = MongoClient(host='dsnotebook.bid', port=27017, username=secret.mongo_user, password=secret.mongo_pwd)

    db=mango['explore']
    coll=db['compare']

except:
    mango = MongoClient(host='dsnotebook.bid', port=27017, username='face', password='rekognition')

    db=mango['explore']
    coll=db['research']    
    print 'no mango'
    

def face2compare(path):
    #collection={}
    if path[-1]!='/':
        path+='/'
    dr=os.listdir(path)
    
    print len(dr), 'files in the folder'
    
    pairs = [(i.split('_cpr.jpg')[0]+'.jpg',i) for i in dr if i.endswith('_cpr.jpg')]
    print 'should be',len(pairs), 'paris'
    flag = raw_input('proceed? y/n ')
    if flag!='y':exit(0)
    print 'pushing...', len(dr)
    
    n=0
    start=time()
    
    for i,j in pairs:
        n+=1
        
        try:

            with open(path+i, 'rb') as image1:
                b1 = image1.read()

            with open(path+j, 'rb') as image2:
                b2 = image2.read()
                
                response = client.compare_faces(SourceImage={'Bytes': b1}, TargetImage={'Bytes': b2}, SimilarityThreshold=0)
                
            print n, i,j,'{:.2f}s'.format(time()-start)
            
        except Exception as e:
            print e
            
        
        #collection['picture_name']=i
        #collection['api_result']=response
        try:
            with open('compare.csv', 'a') as fh:
                one={'pair_root_name':i, 'api_result':response}
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

