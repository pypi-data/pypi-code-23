#!/usr/bin/python
import boto3
import os, socket, time, datetime
import sys, getopt

from ec2 import *
from s3 import *
from config import *
from utils import *


#debug = False
credentials = ''
mode = 'ec2'
list= False
s3bucket = ''
cmd = 'list'
profile = ''
s3_path = ''
file_path = ''
thetag = ''
ip_only = False
key=''
secret=''
qty = 0
ami = DEFAULT_AMI
instance_id = ''
new_tags = ''
filter_tags = ''


def usage():
  print 'aws-cmd.py [-h -d ] [-p profile] [-k key] [-s secret] [-c credentials_file] [-m mode ] [-b bucket] [-C command] [-P s3_path] [-F file_path] [-i instanceid] [-t tag_key:value] [-T tag_key:value] [ -I ] [--ft=tag1,tag2..]'
  print '  -h   - this help'
  print '  -p   - profile (in credential file)  '
  print '  -c   - path to credentials          [default: ~/.aws/credentials]'
  print '  -k   - key (takes precedence over profile)'
  print '  -s   - secret (takes prcedence over profile)'
  print '  -m   - operation mode: ec2|s3       [default: ec2]      '
  print '  ---'
  print '  ec2: options: '
  print '  -i   - instance id '
  print '  -t   - match instances with tag values [tagname:tagvalue,.. ] '
  print '  --ft - Display only tags in comma separated list tag1,tag2.. '
  print '  -I   - list only ip ' 
  print '  -C   - command: list|launch|start|stop|terminate|retag [default: list]'
  print '  -q   - number of instances to launch [default: 0]' 
  print '  -a   - AMI id [default: ' + DEFAULT_AMI  + ']'
  print '  -T   - new tags (for retag command only) [tagname:tagvalue,.. ] '
  print '  ---'
  print '  s3: options: '
  print '  -b   - s3 bucket '
  print '  -l   - list all s3 buckets          [default for s3 mode]'
  print '  -C   - command: S3: list|tree|new|del|put|rm|get [default: list]'
  print '                    list - lists all buckets or given bucket if it exists'
  print '                    tree - recursively lists all objects from S3_path if given, default: / '
  print '                    new  - creates a new s3 bucket'
  print '                    del  - deletes a s3 bucket'
  print '                    put  - adds a s3 object'
  print '                    rm   - removes a s3 object'
  print '                    get  - gets a s3 object'
  print '                    ls   - is object there? '
  print '  -P - s3_path                     '
  print '  -F - file_path                     '
  print '  -d - debug flag'

def getparams():
  global debug, profile, credentials, mode, s3bucket, list, cmd, s3_path, file_path, thetag, ip_only,key,secret,qty,ami,instance_id, new_tags, filter_tags

  try:
    opts, args = getopt.getopt(sys.argv[1:],"hdlIp:c:k:s:m:q:a:b:C:P:F:t:i:T:",["profile=","credentials=","key=","secret=","mode=","qty=", "ami=", "bucket=","cmd=","s3_path=","file_path=","tag=","instance_id=","newtags=","ft="])
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
    elif opt in ("-m", "--mode"):
      mode = arg
    elif opt in ("-q", "--qty"):
      qty = arg
    elif opt in ("-a", "--ami"):
      ami = arg
    elif opt in ("-b", "--bucket"):
      s3bucket = arg
    elif opt in ("-C", "--cmd"):
      cmd = arg
    elif opt in ("-P", "--s3_path"):
      s3_path = arg
    elif opt in ("-F", "--file_path"):
      file_path = arg
    elif opt in ("-d", "--dest"):
      dest = arg
    elif opt in ("-t", "--tag"):
      thetag = arg
    elif opt in ("-I", "--ip"):
      ip_only = True
    elif opt in ("-k", "--key"):
      key = arg
    elif opt in ("-s", "--secret"):
      secret = arg
    elif opt in ("-i", "--instanceid"):
      instance_id = arg
    elif opt in ("-T", "--newtags"):
      new_tags = arg
    elif opt in ("--ft"):
      filter_tags = arg
    elif opt in ("-l"):
      list = True

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

###########################
# MAIN
###########################
def main ():

  getparams()
  sets3debug(False)
  setcredentials()

  if mode == 'ec2':
    do_ec2(cmd,ip_only,thetag,key,secret,ami,qty,instance_id,new_tags,filter_tags)
  elif mode == 's3':
    region=''
    do_s3(cmd, s3bucket, s3_path, file_path,region, key, secret)
  else:
    error('invalid mode')

if __name__ == '__main__':
  main()

#EOF
