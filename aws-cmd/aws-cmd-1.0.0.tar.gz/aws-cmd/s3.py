#!/usr/bin/python
import boto3
import os, socket, time, datetime
import sys, getopt

from config import *
from utils import *

default_region = 'ap-southeast-2'
#debug = False
s3bucket = ''
MAX_OBJECTS = 500
region=DEFAULT_REGION
key=''
secret=''
###################################################
#
# S3 routines
#
###################################################

###################################################
#
# set an optional debug to S3
#
###################################################
def sets3debug(debug):
  if debug:
    boto3.set_stream_logger(name='boto3', level=1)

def s3_connect():
  global debug, region, key, secret
  try:
    if key and secret:
      s3 = boto3.resource('s3', region_name=region,  aws_access_key_id=key, aws_secret_access_key=secret)
    else:
      s3 = boto3.resource('s3', region_name=region  )
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

  return s3


###################################################
#
# create a bucket
#
###################################################
def new_s3(thebucket):
  try:
    s3 = s3_connect()
    config = {'LocationConstraint': default_region }
    s3.create_bucket(Bucket=thebucket, CreateBucketConfiguration=config)
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

###################################################
#
# Delete a bucket
#
###################################################
def delete_s3(thebucket):
  try:
    s3 = s3_connect()
    bucket = s3.Bucket(thebucket)
    for key in bucket.objects.all():
      key.delete()
    bucket.delete()
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)


###################################################
#
# put a file to s3 bucket
#
###################################################
def put_s3(thebucket,src_path,dest_path):
  global debug

  s3 = s3_connect()
  s3.Object(thebucket, dest_path).put(Body=open(src_path, 'rb'))

###################################################
#
# removes a file from s3 bucket
#
###################################################
def rm_s3(thebucket,dest_path):
  global debug
  try:
    s3 = s3_connect()
    s3.Object(thebucket, dest_path).delete()
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)
    

###################################################
#
# gets a objecr from s3 bucket
#
###################################################
def get_s3(thebucket,obj_path,file_path):
  global debug
  try:
    s3 = s3_connect()
#    s3.Object(thebucket, objdest_path).get()
    s3.Bucket(thebucket).download_file(obj_path, file_path)
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)
    
    
###################################################
#
# prints the contents of S3 bucket
#
###################################################
def tree_s3(thebucket,prefix='',exact=False , delimiter=''):
  global debug

  try:
    s3 = s3_connect()
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

  # Print out bucket names
  if debug:
    for bucket in s3.buckets.all():
      print(bucket.name)

  try:
    bucket = s3.Bucket(thebucket)
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

  try:
    if prefix:
      if prefix.endswith('/'):
        exact = False
      else:
        exact = True
      if exact:
        object = bucket.Object(prefix)
        object.load()
        print(object.key)
      else:
        for object in bucket.objects.filter(Prefix=prefix,Delimiter=delimiter):
            if delimiter:
              if object.key.replace(prefix,''): 
                print(object.key.replace(prefix,''))
            else:
              print(object.key)
    else:
#      for object in bucket.objects.all():
#      bucket.objects.page_size(10)
#      for page in bucket.objects.pages():
#          cnt = 0
#          for obj in page:
#            print(obj.key)
#            cnt += 1
#          print 'printed' + str(cnt)
#          response = raw_input("continue [N/y]?")
#          if response == 'n':
#            return

      for object in bucket.objects.limit(MAX_OBJECTS):
          print(object.key)
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

    
###################################################
#
# prints directories only
#
###################################################
def dirs(thebucket,prefix=''):
  global debug

  if not prefix.endswith('/'):
    return

  try:
    s3client = boto3.client('s3',region_name = region)
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

  try:
    o = s3client.list_objects(Bucket=thebucket,Prefix=prefix,Delimiter='/')
    o_list = o.get('CommonPrefixes')
    if o_list:
      for i in o.get('CommonPrefixes'):
        print( i.get('Prefix').replace(prefix,''))
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)


###################################################
#
# list all S3 buckets
#
###################################################
def list_s3(inbucket=''):
  global debug, region, key, secret
  trace ('list_s3() inbucket=' + inbucket)

  s3 = s3_connect()

  # Print out bucket names
  try:
    if inbucket:
      bucket = s3.Bucket(inbucket)
      bucket.load()
      print(bucket.name)
    else:
      for bucket in s3.buckets.all():
        print(bucket.name)
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)


###################################################
#
# main entry into s3 routines
#
###################################################
def do_s3 (cmd='list', s3bucket='', s3_path='', file_path='', inregion='', inkey='', insecret=''):
  trace ('do_s3() cmd=' + cmd + ' bucket=' + s3bucket)
  global key, secret

  if s3bucket == '*':
    s3bucket = ''

  if inregion:
    region=inregion
  if inkey:
    key=inkey
  if insecret:
    secret=insecret

  if not s3bucket:
    list_s3()
    return 0

  if cmd == 'list':
    list_s3(s3bucket)
    return 0

  if cmd == 'tree':
    tree_s3(s3bucket, s3_path )
    return 0

  if cmd == 'files':
    tree_s3(s3bucket, s3_path, True, '/' )
    return 0

  if cmd == 'dirs':
    dirs(s3bucket, s3_path )
    return 0

  if cmd == 'ls':
    dirs(s3bucket, s3_path )
    tree_s3(s3bucket, s3_path, False, '/')
    return 0

  if cmd == 'put':
    put_s3(s3bucket,file_path, s3_path)
    return 0

  if cmd == 'rm':
    rm_s3(s3bucket,s3_path)
    return 0

  if cmd == 'get':
    get_s3(s3bucket,s3_path,file_path)
    return 0

  if cmd == 'new':
    new_s3(s3bucket)
    return 0

  if cmd == 'del':
    response = raw_input("Are you sure you want to delete the entire S3 bucket " + s3bucket + " [N/y]?")
    if response == 'y':
      delete_s3(s3bucket)
    else:
      print "aborting .."
    return 0
    


