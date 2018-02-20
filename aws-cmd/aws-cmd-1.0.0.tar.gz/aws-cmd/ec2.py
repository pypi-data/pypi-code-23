#!/usr/bin/python
import boto3
import os, socket, time, datetime
import sys, getopt
import re

from config import *
from utils import *

show_only_ip = False
line_mode = False
running_only = False
list = False
region=DEFAULT_REGION
instance_type=DEFAULT_INSTANCE_TYPE
key = ''
secret = ''
tags = {}       # A dictionary of list containing tag values
display_tags = {}       # A dictonary of tags to filter in for display

def set_display_tags(thetags=''):
  trace('set_display_tags(' + thetags + ')')
  global display_tags

  tag_list = thetags.split(',')
  for tag in tag_list:
    display_tags[tag] = 1

def flatten_tags (thetags={}):
  flattened_tags = {}
  for tag_name, tag_values in thetags.items():
    for value in tag_values:
      flattened_tags[tag_name] = value
  return flattened_tags

# returns true if in the tags dict
def in_tags(inkey='', invalue=''):
  trace('in_tags(inkey: ' + inkey + ', invalue:' + invalue + ')')
  if not inkey or not invalue:
    return False
  for tag_name, tag_values in tags.items():
    trace('   tag: ' + tag_name )
    if inkey != tag_name:
      continue
    for value in tag_values:
      if re.search ( value, invalue ):
        return True
  return False


# returns true if tag is matched 
def check_tag (instance):
    tag_str = ''
    all_tags = []
    if instance.has_key ("Tags"):
      all_tags = instance[ "Tags" ]
    if not tags:
      return True

    for thetag in all_tags:
      if in_tags (thetag['Key'], thetag['Value']):
        return True
    return False

# process tagkey1:tagvalue1,tagkey2:tagvalue2 .. and put into array desttags
def init_tags (intags='',desttags=''):
#  global tags
  tags = desttags
  tag_pair = intags.split(',')
  for pair in tag_pair:
      pair_splitted = pair.split(':')
      if len(pair_splitted) == 2:
        values = tags.get(pair_splitted[0])
        if values:
            values.append(pair_splitted[1])
        else:
            values=[pair_splitted[1]]
        tags[pair_splitted[0]] = values
#        tags.update( {pair_splitted[0]:pair_splitted[1]} )

def get_tags (instance):
    tag_str = ''
    all_tags = []
    if instance.has_key ("Tags"):
      all_tags = instance[ "Tags" ]
    for tag in all_tags:
      if len(display_tags) > 0:
        if display_tags.has_key (tag['Key']):
          tag_str += ";%s:%s " % (tag['Key'], tag['Value'])
      else:
        tag_str += ";%s:%s " % (tag['Key'], tag['Value'])
    return tag_str

def ec2_connect():
  global debug, region, key, secret
  try:
    if key and secret:
      ec2 = boto3.client('ec2', region_name=region,  aws_access_key_id=key, aws_secret_access_key=secret)
    else:
      ec2 = boto3.client('ec2', region_name=region  )
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)
  return ec2

def list(tag='',region=DEFAULT_REGION ):
  trace('list()')
  global key, secret

  ec2 = ec2_connect()

  try:
  	response = ec2.describe_instances()
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

  for reservation in response["Reservations"]:
#    trace ( "reservation id: %s" % (reservation["ReservationId"]) )
    trace ( "ec2 instances: ")

    for instance in reservation["Instances"]:
      id = instance["InstanceId"]
      if instance.has_key("PublicIpAddress"):
        ip = instance[ "PublicIpAddress"]
      else:
        ip = 'None'
      state = instance[ "State" ]["Name"]
      if not check_tag ( instance ):
        continue
      if line_mode:
        print "%s" % (id)
      else:
#       print instance
        if show_only_ip:
          print "id: %s ; ip: %s" % (id, ip )
        else:
          print "id: %s ; ip: %s ; state: %s ; TAGS:- %s" % (id, ip, state, get_tags(instance))

def launch(qty=0,ami=''):
  trace('launch(qty=' + str(qty) + ', ami=' + ami + 'x)')
  global tags

  ec2 = ec2_connect()

  # IMPT: Ensure that EBS volume will be deleted on instance termination:
  block_device_map = [ { 'DeviceName': '/dev/sda1', 'Ebs': { 'VolumeSize': 9, 'VolumeType': 'standard', 'DeleteOnTermination': True } } ]

  try:
    response =ec2.run_instances(
        ImageId = ami,
        KeyName='acentos.pem',
        InstanceType = instance_type,
        MinCount = qty,
        MaxCount = qty,
        BlockDeviceMappings=block_device_map,
        DryRun=False,
    )
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

  instances = []
  for i in response['Instances']:
    instances.append(i['InstanceId'])
    print "Started " + i['InstanceId']

  # flatten tags
  flattened_tags = flatten_tags(tags)
  tag_list = [ {'Key':'user', 'Value':DEFAULT_USER } ]
  for tag_name, tag_value in flattened_tags.items():
    tag_list.append( { 'Key':tag_name, 'Value':tag_value } )

  try:
    ec2.create_tags( Resources=instances, Tags=tag_list)
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

# Gets a list of instances ids from the supplied tags (in the tags variable) and instanceid
def get_instances(instance_id=''):
  trace('get_instances(instance_id=' + instance_id + ')')

  instances = []
  try:
    ec2 = ec2_connect()
    filter_tags = []
    for tag_name, tag_values in tags.items():
      tag_key = 'tag:'+tag_name
      filter_tags.append( { 'Name':tag_key, 'Values':tag_values } )
    if instance_id:
      response = ec2.describe_instances( Filters=filter_tags, InstanceIds = [ instance_id ] )
    else:
      # WARNING: DO remove the following statement. Doing so will select all instances if there are not tags specified. This
      #          is very dangerous!!
      if not filter_tags:
        return instances
      response = ec2.describe_instances( Filters=filter_tags )
    for r in response['Reservations']:
      for i in r['Instances']:
        instances.append(i['InstanceId'])
        trace('   adding ' + i['InstanceId'])
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)
  return instances

def start(instance_id=''):
  trace('start(instance_id=' + instance_id + ')')

  ec2 = ec2_connect()

  try:
    if instance_id and not tags:
      print 'Starting ' + instance_id
      ec2.start_instances( InstanceIds = [ instance_id ] )
    else:
      instances = get_instances (instance_id)
      for i in instances:
        print "Starting " + i
      ec2.start_instances( InstanceIds = instances )
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)


def stop(instance_id=''):
  trace('stop(instance_id=' + instance_id + ')')

  ec2 = ec2_connect()

  try:
    if instance_id and not tags:
      print 'Stopping ' + instance_id
      ec2.stop_instances( InstanceIds = [ instance_id ] )
    else:
      instances = get_instances (instance_id)
      for i in instances:
        print "Stopping " + i
      ec2.stop_instances( InstanceIds = instances )
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)


def terminate(instance_id=''):
  trace('terminate(instance_id=' + instance_id + ')')

  ec2 = ec2_connect()

  try:
    if instance_id and not tags:
      print 'Terminating ' + instance_id
      ec2.terminate_instances( InstanceIds = [ instance_id ] )
    else:
      instances = get_instances (instance_id)
      for i in instances:
        print "Terminating " + i
      ec2.terminate_instances( InstanceIds = instances )
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)

def retag(instance_id='',in_new_tags=''):
  trace('retag(instance_id=' + instance_id + ')')

  new_tags = {}
  if not in_new_tags:
    return
  else:
    init_tags(in_new_tags,new_tags)

  flattened_tags = flatten_tags(new_tags)

  ec2 = ec2_connect()

  tag_list = [ {'Key':'user', 'Value':DEFAULT_USER } ]
  for tag_name, tag_value in flattened_tags.items():
    tag_list.append( { 'Key':tag_name, 'Value':tag_value } )

  try:
    if instance_id and not tags:
      print 'retagging ' + instance_id
      instances = [ instance_id ]
      ec2.create_tags( Resources=instances, Tags=tag_list)
    else:
      instances = get_instances (instance_id)
      for i in instances:
        print "retagging " + i
      ec2.create_tags( Resources=instances, Tags=tag_list)
  except Exception, e:
    print "failed: " + str(e)
    sys.exit(2)


##########################################################3
#
#   Main entry
#
##########################################################3
def do_ec2(cmd='list',ip_only=False,intags='', inkey='', insecret='', ami='', qty=0, instance_id='', new_tags='', infilter_tags=''):
  trace('do_ec2(ip_only=' + str(ip_only) + ' tags=' + intags + ' instance_id=' + instance_id + ' new_tags=' + new_tags + ' filter_tags=' + infilter_tags + ')')
  global show_only_ip , key, secret, tags
  show_only_ip = ip_only

  init_tags(intags,tags)
 # print tags

  if inkey:
    key = inkey
  if insecret:
    secret = insecret
  if infilter_tags:
    set_display_tags (infilter_tags)

  if cmd=='list':
    list(tags)

  if cmd=='launch':
    launch(int(qty),ami)

  if cmd=='start':
    start(instance_id)

  if cmd=='stop':
    stop(instance_id)

  if cmd=='terminate':
    terminate(instance_id)

  if cmd=='retag':
    retag(instance_id,new_tags)


