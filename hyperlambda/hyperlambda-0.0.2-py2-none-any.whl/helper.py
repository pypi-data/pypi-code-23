# -*- coding: utf-8 -*-

# Licensed to Ecometrica under one or more contributor license
# agreements.  See the NOTICE file distributed with this work
# for additional information regarding copyright ownership.
# Ecometrica licenses this file to you under the Apache
# License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License.  You may obtain a
# copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import (division, print_function,
                        unicode_literals)

from functools import partial
from tempfile import NamedTemporaryFile
import logging
from . import settings
import requests
import json
import boto3
import base64
import requests
import threading
from . import exceptions
import time
import datetime
import traceback
from collections import OrderedDict

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())




class warp_lambda(object):
    """
    A Hyperlambda is a web service that allows a client to securely supply an algorithm, 
    which the server will evaluate on its side, and (optionally) return the results of its evaluation back to the client. 
    This completely reverses the responsibility between the “client” and the “server”, and allows for a whole range of really interesting scenarios, 
    arguably facilitating for that your machines can engage in a “meaningful semantic discussion”, 
    communicating intent back and forth, the same way two human beings can.
    """
    def __init__(self, description="hyperlambda Function",version=1.0,verbose=1,function_name=None,region=settings.region,zip_file=None,code=None,role=None,handler=None,runtime='python2.7',
                        timeout=180,data={},environment=None,userdata='',tags=None,security_group_ids=settings.security_group_ids,key_name=settings.key_name,callback_url=None,
                        aws_access_key_id=settings.aws_access_key_id,aws_secret_access_key=settings.aws_secret_access_key,instance_type=settings.instance_type,image_id=settings.image_id,spot_price = settings.spot_price):
        
        self.description = description

        self.function_name = function_name
        self.region = region
        self.zip_file=zip_file
        self.code=code
        self.role = role
        self.handler=handler
        self.runtime = runtime
        self.timeout = timeout
        self.data = data
        self.environment = environment
        self.userdata = userdata
        self.tags = tags
        self.security_group_ids= security_group_ids
        self.key_name = key_name
        self.callback_url = callback_url
        self.spot_price = spot_price

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.instance_type = instance_type
        self.image_id = image_id
        self.created_time = datetime.datetime.now()
        self.started_time = None
        self.finishedtime = None

        self.message = 'reequest accepted'
        self.state = 'initial'
        self.response = None

        self.timeout_terminate = False



        self.client = boto3.client(
            'ec2',
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        self.ec2 = boto3.resource('ec2', self.region, aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)

        logging.info('HyperLambda Initializing... ')

        
    def create_bash(self):
        user_data = '#!/bin/bash\n'
        if self.environment !=None:
            for key,itm in self.environment['Variables'].iteritems():
                user_data+="echo "+key+"="+'"'+str(itm)+'"'+" >> "+" /etc/environment \n"
        return user_data

    def create_instance(self):
        logging.info("bidding for instance ")
        self.message = 'Instance Creating'
        self.state = 'pending'

        instance_arg = dict(
            InstanceCount=1,
            LaunchSpecification=dict(
                BlockDeviceMappings=[
                    dict(
                        DeviceName='/dev/sda1',
                        Ebs=dict(
                            VolumeSize=settings.volume_size,
                            VolumeType='gp2'
                            )
                    )
                ],
                ImageId= settings.image_id,
                InstanceType=self.instance_type,
                SecurityGroupIds=self.security_group_ids,
                UserData=base64.b64encode(self.create_bash()+settings.user_data.format(self.runtime,self.runtime)+"\n"+self.userdata)
            ),
            Type='one-time',
            SpotPrice=self.spot_price
        )
        
        if self.key_name:
            instance_arg['LaunchSpecification']['KeyName']=settings.key_name

        logging.debug(instance_arg)

        response=self.client.request_spot_instances(**instance_arg)

        
        # print (response) # {u'SpotInstanceRequests': [{u'Status': {u'Message': 'Your Spot request has been submitted for review, and is pending evaluation.', u'Code': 'pending-evaluation', u'UpdateTime': datetime.datetime(2017, 6, 19, 6, 49, 16, tzinfo=tzutc())}, u'ProductDescription': 'Linux/UNIX', u'SpotInstanceRequestId': 'sir-rryin8jm', u'State': 'open', u'LaunchSpecification': {u'Placement': {u'AvailabilityZone': 'ap-south-1a'}, u'ImageId': 'ami-a35e21cc', u'KeyName': 'processing-node', u'SecurityGroups': [{u'GroupName': 'processing_child', u'GroupId': 'sg-542cc23c'}], u'SubnetId': 'subnet-eeebaa87', u'Monitoring': {u'Enabled': False}, u'InstanceType': 'm4.large'}, u'Type': 'one-time', u'CreateTime': datetime.datetime(2017, 6, 19, 6, 49, 16, tzinfo=tzutc()), u'SpotPrice': '0.003000'}], 'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': '44134098-b24f-4c71-8385-3630cc8f3ef4', 'HTTPHeaders': {'transfer-encoding': 'chunked', 'vary': 'Accept-Encoding', 'server': 'AmazonEC2', 'content-type': 'text/xml;charset=UTF-8', 'date': 'Mon, 19 Jun 2017 06:49:15 GMT'}}}
        logging.info(response['SpotInstanceRequests'][0]['Status']['Message'])
        spot_instance_id = None
        spot_instance_req_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
        if response['SpotInstanceRequests'][0]['State']=='active':
            spot_instance_id = response['SpotInstanceRequests'][0]['InstanceId']
        elif response['SpotInstanceRequests'][0]['State'] == 'open':
            if response['SpotInstanceRequests'][0]['Status']['Code']== 'pending-evaluation' or response['SpotInstanceRequests'][0]['Status']['Code']== 'pending-fulfillment':
                try:
                    logging.info("Waiting for the spot instance request to be fullfilled")
                    waiter = self.client.get_waiter('spot_instance_request_fulfilled')
                    waiter.wait(SpotInstanceRequestIds=[spot_instance_req_id, ])
                except Exception,e:
                    logging.debug(e.message)

                instance_req = self.client.describe_spot_instance_requests(SpotInstanceRequestIds=[response['SpotInstanceRequests'][0]['SpotInstanceRequestId']])
                # {u'SpotInstanceRequests': [{u'Status': {u'Message': 'Your Spot request is fulfilled.', u'Code': 'fulfilled', u'UpdateTime': datetime.datetime(2017, 6, 19, 7, 30, 28, tzinfo=tzutc())}, u'ActualBlockHourlyPrice': '0.093000', u'InstanceId': 'i-05e232340e5379810', u'BlockDurationMinutes': 60, u'SpotInstanceRequestId': 'sir-w5wip7rn', u'State': 'active', u'ProductDescription': 'Linux/UNIX', u'LaunchedAvailabilityZone': 'ap-south-1a', u'LaunchSpecification': {u'Placement': {u'AvailabilityZone': 'ap-south-1a'}, u'ImageId': 'ami-a35e21cc', u'KeyName': 'processing-node', u'SecurityGroups': [{u'GroupName': 'processing_child', u'GroupId': 'sg-542cc23c'}], u'SubnetId': 'subnet-eeebaa87', u'Monitoring': {u'Enabled': False}, u'InstanceType': 'm4.large'}, u'Type': 'one-time', u'CreateTime': datetime.datetime(2017, 6, 19, 7, 30, 20, tzinfo=tzutc()), u'SpotPrice': '0.093000'}], 'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': 'eba4458f-c142-4b1a-8b10-4c27a0e8a962', 'HTTPHeaders': {'transfer-encoding': 'chunked', 'vary': 'Accept-Encoding', 'server': 'AmazonEC2', 'content-type': 'text/xml;charset=UTF-8', 'date': 'Mon, 19 Jun 2017 08:09:41 GMT'}}}
                if instance_req['SpotInstanceRequests'][0]['State'] == 'active':
                    spot_instance_id = instance_req['SpotInstanceRequests'][0]['InstanceId']

                    logging.info(instance_req['SpotInstanceRequests'][0]['Status']['Message'])


        if spot_instance_id:
            reservations = self.client.describe_instances(InstanceIds=[spot_instance_id])
            if reservations:
                ip_address = reservations['Reservations'][0]['Instances'][0]['PublicIpAddress']
                logging.info("PublicIpAddress: "+ip_address)
                instance_obj = self.ec2.Instance(reservations['Reservations'][0]['Instances'][0]['InstanceId'])
                instance_obj.create_tags(Tags=[{'Key': 'Name', 'Value': self.function_name}]) # name instance
                self.instance = {'ip_address':ip_address,'instance_req_id':spot_instance_req_id,"instance_id":spot_instance_id}
                logging.info("Waits until this instance {} is exists".format(spot_instance_id))
                instance_obj.wait_until_exists()
                logging.info("Waits until this instance {} is running".format(spot_instance_id))
                instance_obj.wait_until_running()
                logging.info("Instance Started Running")
                
                logging.debug(self.instance)

                self.thread_terminate_timeout_instance = threading.Timer(self.timeout+60,self.terminate_instance,[True])
                self.thread_terminate_timeout_instance.start()

                self.message = "Your Instance is created"
                self.state = 'queued'

                return True
        else:
            logging.debug("Cancelling Spot Instance Request with error message: {}".format(instance_req['SpotInstanceRequests'][0]['Status']['Message']))
            instance_req = self.client.describe_spot_instance_requests(SpotInstanceRequestIds=[response['SpotInstanceRequests'][0]['SpotInstanceRequestId']])
            logging.info(instance_req['SpotInstanceRequests'][0]['Status']['Message'])

            self.client.cancel_spot_instance_requests(SpotInstanceRequestIds=[spot_instance_req_id])
            
            self.message = instance_req['SpotInstanceRequests'][0]['Status']['Message']
            self.State = 'cancelled' 
            self.finishedtime = datetime.datetime.now()

        return False


    def execute_lambda(self):
        try:
            data = {'url':self.zip_file,'handler':self.handler,'payload':self.data,'callback_url':self.callback_url}
            logging.debug(data)
            logging.debug("sending script for processing...")
            self.started_time = datetime.datetime.now()
            try:
                post_req = requests.post("http://"+self.instance['ip_address']+"/lambda_processing/", data=json.dumps(data))
            except Exception,e:
                logging.info(e.message)
                self.message = "Sending Request failed, will try again."
                self.state = 'delayed'
                time.sleep(30)
                post_req = requests.post("http://"+self.instance['ip_address']+"/lambda_processing/", data=json.dumps(data))
            
            response = post_req.json()

            if post_req.status_code == 202:
                self.message = response['message']
                self.state = response['status']
                self.response = response.get('response',None)
                logging.info("Request Accepted for processing")
                exec_status = self.check_instance()
                return exec_status
            else:
                logging.info("client server rejected requests")
                self.message = response['message']
                self.state = 'cancelled'
                self.terminate_instance(timeout=False)
                
                self.finishedtime = datetime.datetime.now()
                duration = self.finishedtime - self.started_time
                logging.error("HyperLambda script Execution Failed with time duration of {} seconds with error message: {}".format(duration.total_seconds(),self.message))
                return 1
        
        except exceptions.FunctionTimeoutError,e:
            self.finishedtime = datetime.datetime.now()
            raise exceptions.FunctionTimeoutError(timeout=self.timeout)

        except exceptions.InstanceTerminatedError,e:
            self.finishedtime = datetime.datetime.now()
            raise exceptions.InstanceTerminatedError(message=e.message)

        except Exception,e:
            logging.info("Something went wrong with error message: {}".format(e.message))
            self.message = e.message
            self.state = 'cancelled'
            self.terminate_instance(timeout=False)
            self.finishedtime = datetime.datetime.now()
            duration = self.finishedtime - self.started_time
            logging.error("HyperLambda script Execution Failed with time duration of {} seconds with error message: {}".format(duration.total_seconds(),self.message))
            return 1





    def check_instance(self):
        try:
            response = self.client.describe_instance_status(InstanceIds=[self.instance['instance_id'],],IncludeAllInstances=True)
            if response['InstanceStatuses'][0]['InstanceState']['Name'] != 'running':
                if self.timeout_terminate == True:
                    self.message = "{} Task timed out after {} seconds".format(self.function_name,self.timeout)
                    self.state = 'timeout'
                    raise exceptions.FunctionTimeoutError(timeout=self.timeout)
                else:
                    if self.instance['spot_instance_req_id']:
                        response = self.client.describe_spot_instance_requests(
                                        SpotInstanceRequestIds=[self.instance['spot_instance_req_id'],],)

                        self.terminate_instance()
                        self.message = response['SpotInstanceRequests'][0]['Status']['Code']['Message']
                        self.state = 'failed'
                        raise exceptions.InstanceTerminatedError(message=response['SpotInstanceRequests'][0]['Status']['Code']['Message'])
                    else:
                        instance_response = self.client.describe_instances(InstanceIds=[self.instance['instance_id']])
                        self.terminate_instance()
                        self.message = instance_response['Reservations'][0]['Instances'][0]['StateReason']
                        self.state = 'failed'
                        raise exceptions.InstanceTerminatedError(message=instance_response['Reservations'][0]['Instances'][0]['StateReason'])

            else:
                try:
                    get_req = requests.get("http://"+self.instance['ip_address']+"/lambda_status/")

                    if get_req.status_code ==200:
                        result = get_req.json()
                        self.message = result['message']
                        self.state = result['status']
                        self.response = result.get('response',None)

                except Exception,e:
                    logging.debug(e.message)

                if self.state == 'success':
                    self.terminate_instance()
                    self.finishedtime = datetime.datetime.now()
                    duration = self.finishedtime - self.started_time
                    logging.info("HyperLambda script Execution completed successfully with time duration of {} seconds with response: {}".format(duration.total_seconds(),self.response))
                    
                    return 0
                elif self.state == 'failed':
                    self.terminate_instance()
                    self.finishedtime = datetime.datetime.now()
                    duration = self.finishedtime - self.started_time
                    logging.error("HyperLambda script Execution Failed with time duration of {} seconds with error message: {}".format(duration.total_seconds()),self.message)
                    self.finishedtime = datetime.datetime.now()
                    return 1

                else:
                    time.sleep(20)
                    self.check_instance()
        
        except exceptions.FunctionTimeoutError,e:
            self.finishedtime = datetime.datetime.now()
            raise exceptions.FunctionTimeoutError(timeout=self.timeout)

        except exceptions.InstanceTerminatedError,e:
            self.finishedtime = datetime.datetime.now()
            raise exceptions.InstanceTerminatedError(message=e.message)

        except Exception,e:
            logging.debug(e.message)
            self.finishedtime = datetime.datetime.now()
            duration = self.finishedtime - self.started_time
            logging.info("Failed with time duration of {} seconds with error message: {}".format(duration.total_seconds(),e.message))
            return 1


    def terminate_instance(self,timeout=False):
        try:
            if self.instance['instance_req_id']:
                self.client.cancel_spot_instance_requests(SpotInstanceRequestIds=[self.instance['instance_req_id']])

            self.client.terminate_instances(InstanceIds=[self.instance['instance_id']])

            self.timeout_terminate = timeout
            if timeout:
                logging.info("Timeout of {} seconds reached. Closed the instance".format(self.timeout))
                self.check_instance()
            else:
                logging.info("Instance Closed Successfully")

        except Exception,e:
            logging.debug(e.message)

    def lambda_status(self):
        try:
            instance_response = self.client.describe_instances(InstanceIds=[self.instance['instance_id']])
            instance_details = instance_response['Reservations'][0]['Instances'][0]

            response = dict(
                HyperLambda = [
                    dict(Status = dict(
                        Message = self.message,
                        State = self.state,
                        RequestedTime = datetime.datetime.now(),
                        Response = self.response
                        ),
                    Configuration = dict(
                        FunctionName = self.function_name,
                        Runtime = self.runtime,
                        Role = self.role,
                        ZipFile = self.zip_file,
                        Handler = self.handler,
                        Data = self.data,
                        TimeOut = self.timeout,
                        Environment = self.environment,
                        SecurityGroupIds = self.security_group_ids,
                        KeyName = self.key_name,
                        CallbackURL = self.callback_url,
                        InstanceType = self.instance_type,
                        CreatedTime = self.created_time,
                        StartedTime = self.started_time,
                        FinishedTime = self.finishedtime
                        ),
                    Instance=dict(
                        InstanceType = instance_details['InstanceType'],
                        ImageId = instance_details['ImageId'],
                        KeyName = instance_details['KeyName'],
                        SecurityGroups = instance_details['SecurityGroups'],
                        SpotPrice = self.spot_price,
                        PublicIpAddress = instance_details['PublicIpAddress'],
                        LaunchTime = instance_details['LaunchTime'],
                        SpotInstanceRequestId = instance_details['SpotInstanceRequestId'],
                        InstanceId = instance_details['InstanceId'],
                        Status = instance_details['State']['Name'],


                        )
                    )
                ])

            return response
        
        except Exception,e:
            logging.debug(e.message)
            response = dict(
                HyperLambda = [
                    dict(Status = dict(
                        Message = self.message,
                        State = self.state,
                        RequestedTime = datetime.datetime.now(),
                        Response = self.response
                        ),
                    Configuration = dict(
                        FunctionName = self.function_name,
                        Runtime = self.runtime,
                        Role = self.role,
                        ZipFile = self.zip_file,
                        Handler = self.handler,
                        Data = self.data,
                        TimeOut = self.timeout,
                        Environment = self.environment,
                        SecurityGroupIds = self.security_group_ids,
                        KeyName = self.key_name,
                        CallbackURL = self.callback_url,
                        InstanceType = self.instance_type,
                        CreatedTime = self.created_time,
                        StartedTime = self.started_time,
                        FinishedTime = self.finishedtime
                        )
                    )
                ])
            return response

                
