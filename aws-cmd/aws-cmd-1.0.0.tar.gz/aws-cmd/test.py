#!/usr/bin/python
import boto3
import os, socket, time, datetime
import sys, getopt

from ec2 import *
from s3 import *
from utils import *


DEFAULT_AMI = 'ami-6acfd409'
DEFAULT_REGION = 'ap-southeast-2'
DEFAULT_INSTANCE_TYPE = 't2.micro'
DEFAULT_USER = 'swong'


debug = False
credentials = ''
mode = 'ec2'
region = DEFAULT_REGION
s3bucket = ''
profile = ''
key=''
secret=''
ami = DEFAULT_AMI
elb = None
ec2 = None
ec2_resource = None
tg = None
vpc_id = ''


def usage():
  print 'test.py [-h -d ] [-p profile] [-k key] [-s secret] [-c credentials_file] '
  print '  -h - this help'
  print '  -p - profile (in credential file)  '
  print '  -c - path to credentials          [default: ~/.aws/credentials]'
  print '  -k - key (takes precedence over profile)'
  print '  -s - secret (takes prcedence over profile)'
  print '  -d - debug flag'

def getparams():
  global debug, profile, credentials, mode, s3bucket, list, cmd, s3_path, file_path, thetag, ip_only,key,secret,qty,ami,instance_id, new_tags

  try:
    opts, args = getopt.getopt(sys.argv[1:],"hdp:c:k:s:",["profile=","credentials=","key=","secret="])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      usage()
      sys.exit()
    elif opt in ("-d"):
      debug = True
      debug_on()
    elif opt in ("-p", "--profile"):
      profile = arg
    elif opt in ("-c", "--credentials"):
      credentials = arg
    elif opt in ("-k", "--key"):
      key = arg
    elif opt in ("-s", "--secret"):
      secret = arg

###################################################
#
# set the location of AWS credentials file into
# the enviroment
#
###################################################
def setcredentials():
  global profile, credentials
  if profile:
    if debug:
      print 'setting profile to ' + profile
    os.environ["AWS_PROFILE"] = profile

  if credentials:
    if debug:
      print 'setting credentials to ' + credentials
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = credentials

###################################################
#
# Returns the date in YYYY_MM_DD format
#
###################################################
def getdate():
  ts = time.time()
  st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
  return(st)

def connect_client (type='ec2'):
  _connection = None
  try:
    if key and secret:
      _connection = boto3.client(type, region_name=region,  aws_access_key_id=key, aws_secret_access_key=secret)
    else:
      _connection = boto3.client(type, region_name=region  )
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)
  return _connection

def connect_resource (type='ec2'):
  _connection = None
  try:
    if key and secret:
      _connection = boto3.resource(type, region_name=region,  aws_access_key_id=key, aws_secret_access_key=secret)
    else:
      _connection = boto3.resource(type, region_name=region  )
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)
  return _connection


def show_vpcs ():
  global vpc_id
  vpcs = ec2_resource.vpcs.all()
  for vpc in vpcs:
    vpc_id = vpc.id
    print vpc.id


def run_tg_test ():
  print "run_tg_test()"
  global tg
  tg = elb.create_target_group(
            Name='swong-test-targetgroup',
            Protocol='HTTPS',
            Port=50000,  # placeholder
            VpcId=vpc_id,
            HealthCheckProtocol='HTTPS',
            HealthCheckIntervalSeconds=5,
            HealthCheckTimeoutSeconds=4,
            HealthyThresholdCount=10,
            UnhealthyThresholdCount=2,
            Matcher={
                'HttpCode': '200'
            }
        )
  trn =  tg.get('TargetGroups')[0].get('TargetGroupArn')

  elb.modify_target_group_attributes(
            TargetGroupArn=trn,
            Attributes=[{
                'Key': 'deregistration_delay.timeout_seconds',
                'Value': '180'
            }]
        )


###########################
# MAIN
###########################
def main ():

  global ec2, elb, ec2_resource

  getparams()
  sets3debug(False)
  setcredentials()
  ec2=connect_client('ec2')
  ec2_resource=connect_resource('ec2')
  show_vpcs()
  elb=connect_client('elbv2')
#  run_tg_test()


if __name__ == '__main__':
  main()

#EOF
