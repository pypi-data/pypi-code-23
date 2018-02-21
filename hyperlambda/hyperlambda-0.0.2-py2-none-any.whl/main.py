#!/usr/bin/env python
from __future__ import (division, print_function,
                        unicode_literals)
import argparse
import os
from shutil import copyfileobj
import sys
from tempfile import NamedTemporaryFile
import ConfigParser
import json
from . import exceptions
import logging
import traceback
import time
import base64



class StoreNameValuePair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        
        parsed_conf = {}
        for pair in values[0].split(","):
            key, value = pair.split('=')
            parsed_conf[key] = value
        
        setattr(namespace, 'tags', parsed_conf)

class ValidateNameValuePair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        
        parsed_conf = None
        if 'Variables' in values and isinstance(values['Variables'],(dict)):
            parsed_conf = values
        else:
            parser.error('invalid environment arguments')
            
        setattr(namespace, 'environment', parsed_conf)

class ValidateListValues(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        parsed_conf = None
        if values !=None and isinstance(values,(list)):
            parsed_conf = values
        else:
            parser.error('invalid security_group_ids input type. argument should be a list')
        
        setattr(namespace, 'security_group_ids', parsed_conf)

class ReadDataFromFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        parsed_conf = ''
        if values !=None and os.path.isfile(values):
            with open(values) as file:
                parsed_conf = file.read().strip()

        setattr(namespace, 'userdata', parsed_conf)


def parse_args(args):
    """Parses command-line `args`"""
    from . import settings

    parser = argparse.ArgumentParser(
        description='Create  a Hyper Lambda Instance to Execute Script',
    )
    parser.add_argument('-v', '--verbose', action='count',default=1,
                        help='explain what is being done')

    group = parser.add_argument_group(title=' metadata arguments')
    group.add_argument('--function-name', default=None,required=True,
                       help=('Human-readable name of the function. '
                             ))
    group.add_argument('--description', default="",
                       help='Description of the function. Defaults to ""')
    
    group.add_argument('--version', default='1.0.0',
                       help='Version of the metadata. Defaults to "1.0.0"')
    

    group = parser.add_argument_group(title=' warp arguments')
    group.add_argument('--runtime', default='python2.7',
                       help=('The runtime environment for the Lambda function you are uploading. '
                             'Defaults to python2.7'))
    group.add_argument('--role',type=str,
                       help=('The Amazon Resource Name (ARN) of the IAM role that Lambda assumes when it executes your function to access any other Amazon Web Services (AWS) resources '
                             ))
    group.add_argument('--timeout', type=int,default=180,
                       help=('The function execution time at which Lambda should terminate the function. The Default is 180 seconds '))
    group.add_argument('--handler', required=True,
                       help=('The function within your code that Lambda calls to begin execution. '
                             ))
    group.add_argument('--code',
                       help=('The code for the Lambda function. '
                             ))
    group.add_argument('--zip-file',
                       help=('The URL to the zip file of the code you are uploaded '
                             ))
    group.add_argument('--data', type=json.loads,help=('A dictionary that you want to provide to your Lambda function as input.'))
    group.add_argument('--environment', type=json.loads,default=None, action=ValidateNameValuePair,
                       help=("The parent object that contains your environment's configuration settings. "
                             ))
    group.add_argument('--userdata',default='', action=ReadDataFromFile,
                       help=("The location of the userdata file for the instance. eg: userdata.txt "
                             ))
    group.add_argument('--tags',nargs='*', action=StoreNameValuePair,
                       help=("The list of tags (key-value pairs) assigned to the new function."
                             ))

    group = parser.add_argument_group(title=' instance arguments')
    # group.add_argument('--image-id',
    #                     help=("The ID of the AMI"
    #                         ))
    group.add_argument('--instance-type',type=str,default=settings.instance_type,
                        help=("The type of the instance to be created"
                            ))
    group.add_argument('--key-name',type=str,default=settings.key_name,
                        help=("The name of the key pair"
                            ))
    group.add_argument('--security-group-ids',action=ValidateListValues,default=settings.security_group_ids,
                        help=("One or more security group ids"
                            ))
    group.add_argument('--callback-url',type=str,
                        help=("Optional URL to be called after execution."
                            ))


    args = parser.parse_args(args=args)


    if args.zip_file is None and args.code is None:
        parser.error('must provide --zip-file or --code')
    
    return args


class HyperLambda(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Create  a Hyper Lambda Instance to Execute Script',
            usage='''hyperlambda <command> [<args>]
            The most commonly used hyperlambda commands are:
            configure     Configure the settings
            invoke_function      create and execute lambda function
            ''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print ('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def configure(self):

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # If you want to add new values to prompt, update this list here.
        VALUES_TO_PROMPT_CREDENTIAL = [
        # (logical_name, config_name, prompt_text)
        ('aws_access_key_id', "AWS Access Key ID"),
        ('aws_secret_access_key', "AWS Secret Access Key"),
        ('region', "Default region name")
        ]
        VALUES_TO_PROMPT_INSTANCE = [
        ('security_group_ids',"Security Group Ids<list>"),
        ('key_name', "key Name"),
        ('volume_size', "Volume Size(GiB)"),
        ('instance_type', "Instance Type"),
        ('spot_price',"Spot Price")
        ]

        configfile_name = "config.ini"
        # Check if there is already a configurtion file
        if not os.path.isfile(os.path.join(BASE_DIR,'data',configfile_name)):
            # Create the configuration file as it doesn't exist yet
            cfgfile = open(os.path.join(BASE_DIR,'data',configfile_name), 'w')
            
            # Add content to the file
            Config = ConfigParser.ConfigParser()
            Config.add_section('aws_credentials')
            for itm in VALUES_TO_PROMPT_CREDENTIAL:
                Config.set('aws_credentials', itm[0], raw_input(itm[1]+": "))

            Config.add_section('instance_settings')
            for itm in VALUES_TO_PROMPT_INSTANCE:
                Config.set('instance_settings', itm[0], raw_input(itm[1]+": "))
            

            Config.write(cfgfile)
            cfgfile.close()


    def invoke_function(self, use_logging=True):

        args = parse_args(sys.argv[2:])

        if use_logging:
            configure_logging(args)
        # print (args)
        # HACK: Import here, so that VIPS doesn't parse sys.argv!!!
        # In vimagemodule.cxx, SWIG_init actually does argument parsing
        from .helper import warp_lambda

        lambda_object = warp_lambda(**vars(args))
        try:
            created = lambda_object.create_instance()
        
            if created:
                time.sleep(60) ## waiting for the instance server to be ready to receive requests.
                exec_status = lambda_object.execute_lambda()
            else:
                raise exceptions.NoInstanceCreated(message=lambda_object.message)
        
            lambda_object.thread_terminate_timeout_instance.cancel()

            return exec_status
        except Exception,e:
            print(e)
            traceback.print_exc() 
            return 1

 
def configure_logging(args):
    if not args.verbose:
        return

    if args.verbose == 1:
        level = logging.INFO
        fmt = '[%(asctime)s] [%(levelname)s] : %(message)s'
    else:
        level = logging.DEBUG
        fmt = '[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)s] : %(message)s'

    logging.basicConfig(level=level, format=fmt,
                        datefmt='%Y-%m-%d %H:%M:%S')   


if __name__ == '__main__' and __package__ is None:
    HyperLambda()