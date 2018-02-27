#!/usr/bin/env python
import sys
import boto3
import vmtools

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *

class Main():
    """Class to manipulate aws ec2 resources

    instance variables:
    self.aws_profile
    self.aws_region
    self.session
    self.client_ec2
    self.availability_zones_list
    """

    def __init__(self, aws_profile, aws_region):
        """set instance variables, set instance aws connections

        keyword arguments:
        :type aws_profile: string
        :param aws_profile: the profile to use from ~/.aws/credentials to connect to aws
        :type aws_region: string
        :param aws_region: the region to use for the aws connection object (all resources will be created in this region)
        """
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        # aws session
        self.session = boto3.Session(profile_name=self.aws_profile)
        # ec2 aws client
        self.client_ec2 = self.session.client('ec2', region_name=self.aws_region)
        # aws ec2 object (mainly used for creating and modifying resources)
        self.ec2 = self.session.resource('ec2', region_name=self.aws_region)
        # create a list of available availability zones
        availability_zones_state_dict = self.client_ec2.describe_availability_zones()
        self.availability_zones_list = []
        for availability_zone_dict in availability_zones_state_dict['AvailabilityZones']:
            if availability_zone_dict['State'] == 'available':
                self.availability_zones_list.append(availability_zone_dict['ZoneName'])

    def create_object_type_variables(self, object_type):
        """Take aws object_type and return tuple of (object_type_singular, object_type_plural)
        keyword arguments:
        :type object_type: string
        :param object_type: the type of object it is (ex instance, vpc, subnet etc)
        """
        # create object type for boto3 (object_types should end in 's') and messaging
        if object_type.endswith('s'):
            object_type_plural = object_type
            object_type_singular = object_type[:-1]
        else:
            object_type_plural = '{}s'.format(object_type)
            object_type_singular = object_type
        return (object_type_singular, object_type_plural)

    def analysis_aws_object_lookup_result(self, result, object_type, name, fail_condition=None):
        """Take the result from a aws object lookup, object_type, name and fail_condition (optional), fail or return the aws object
        keyword arguments:
        :type result: list
        :param result: the result of an aws object lookup (ex ec2.instances.filter(Filters=filters)) 
        :type object_type: string
        :param object_type: the type of object it is (ex instance, vpc, subnet etc)
        :type name: string
        :param name: the name of the object (usually tag name)
        :type fail_condition: string
        :param fail_condition: the condition which will cause this function to error and exit the program. possible values are: exists (fail if the object exists), doesnt_exist (fail if the object doesn't exisit), or None (if the object exists, return object, if it doesn't return None)
        """
        object_type_singular, object_type_plural = self.create_object_type_variables(object_type=object_type)
        if result:
            if len(result) == 1:
                aws_object = result[0]
                if fail_condition == 'exists':
                    fail_on_exists_message = 'Failure: A(n) {} with tag name "{}" already exists (object listed below). Botohelper requires "Name tags" to be unique. Quitting...\n{}'.format(object_type_singular, name, result)
                    print(fail_on_exists_message)
                    sys.exit(1)
            else:
                too_many_objects_message = 'Failure: filtering {} by tag name "{}" resulted in more than one {} objects (listed below). Botohelper requires "Name tags" to be unique. Quitting...\n{}'.format(object_type_plural, name, object_type_singular, result)
                print(too_many_objects_message)
                sys.exit(1)
        else:
            if fail_condition == 'doesnt_exist':
                fail_on_doesnt_exists_message = 'Failure: Could not find a {} with tag name "{}". Quitting...\n'.format(object_type_singular, name)
                print(fail_on_doesnt_exists_message)
                sys.exit(1)
            aws_object = None
        return aws_object

