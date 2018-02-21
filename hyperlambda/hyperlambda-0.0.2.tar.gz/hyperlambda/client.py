#!/usr/bin/env python
from __future__ import (division, print_function,
                        unicode_literals)
import os
from shutil import copyfileobj
import sys
from tempfile import NamedTemporaryFile
import ConfigParser
import json
from . import exceptions
import threading
import time
import settings

class lamda(object):
    
    def __init__(self, aws_access_key_id=settings.aws_access_key_id, aws_secret_access_key=settings.aws_secret_access_key,
                 region=settings.region):

        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key=aws_secret_access_key
    

    def invoke_function(self,function_name=None,runtime='python2.7',role=None,timeout=180,handler=None,code=None,zip_file=None
                            ,data=None,environment=None,userdata='',tags=None,instance_type=settings.instance_type,key_name=settings.key_name,security_group_ids=settings.security_group_ids,callback_url=None):

        if function_name is None:
            raise exceptions.NoFunctionError()
        elif not isinstance(timeout, (int, long)):
            raise exceptions.InvalidTimeoutError()
        elif handler is None:
            raise exceptions.NoHandlerError()
        elif handler and isinstance(handler,(dict)):
            raise exceptions.InvalidHandlerError()
        elif code==None and zip_file ==None:
            raise exceptions.NoScriptError()
        elif data !=None and not isinstance(data,(dict)):
            raise exceptions.NoValidDataTypeError()
        elif environment !=None:
            if isinstance(environment,(dict)):
                if 'Variables' in environment and isinstance(environment['Variables'],(dict)):
                    pass
                else:
                    raise exceptions.NoValidDictionaryError()    
            else:
                raise exceptions.NoValidDictionaryError()
        elif tags !=None and isinstance(tags,(dict)):
            raise exceptions.NoValidTagsDictionaryError()
        elif not isinstance(security_group_ids,(list)):
            raise exceptions.InvalidSecurityGroupIdsTypeError()
        elif key_name!=None and not isinstance(key_name,(str,unicode)):
            raise exceptions.InvalidKeyNameTypeError()

        self.kwargs = dict(
                        function_name=function_name,
                        runtime = runtime,
                        role=role,
                        timeout=timeout,
                        handler=handler,
                        code=code,
                        zip_file=zip_file,
                        data=data,
                        environment=environment,
                        userdata=userdata,
                        tags=tags,
                        instance_type=instance_type,
                        key_name=key_name,
                        security_group_ids=security_group_ids,
                        callback_url=callback_url
                    )

        from .helper import warp_lambda

        lambda_object = warp_lambda(region=self.region,aws_access_key_id=self.aws_access_key_id,aws_secret_access_key=self.aws_secret_access_key,**self.kwargs)
        
        self.lamda = lambda_object
        self.exec_thread = threading.Thread(target=self.execute_function)
        self.exec_thread.start()

        
        return lambda_object.lambda_status()
    

    def execute_function(self):
        try:
            created = self.lamda.create_instance()
        
            if created:
                time.sleep(60)  ## waiting for the instance server to be ready to receive requests.
                self.lamda.execute_lambda()
                self.lamda.thread_terminate_timeout_instance.cancel()
            else:
                raise exceptions.NoInstanceCreated(message=self.lamda.message)
        except AttributeError,e:
            raise exceptions.NoFunctionError(message='invoke_function should be called before the operation ')
    
    def describe_function(self):
        try:
            return self.lamda.lambda_status()
        except AttributeError,e:
            raise exceptions.NoFunctionError(message='invoke_function should be called before the operation ')

    def wait_until_completed(self):
        try:
            self.exec_thread.join()
        except AttributeError,e:
            raise exceptions.NoFunctionError(message='invoke_function should be called before the operation ')
        return self.lamda.lambda_status()






