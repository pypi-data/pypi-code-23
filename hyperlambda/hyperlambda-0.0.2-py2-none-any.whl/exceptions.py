# Copyright (c) 2012-2013 Mitch Garnaat http://garnaat.org/
# Copyright 2012-2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from __future__ import unicode_literals
import exceptions

class HyperLambdaError(Exception):
    """
    The base exception class for Hyperlambda exceptions.

    :ivar msg: The descriptive message associated with the error.
    """
    fmt = 'An unspecified error occurred'

    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        Exception.__init__(self, msg)
        self.kwargs = kwargs


class NoFunctionError(HyperLambdaError):
    """No region was specified."""
    fmt = 'You must specify a Function_name.'

class InvalidTimeoutError(HyperLambdaError):
    """Invalid Timeout was specified."""
    fmt = 'You must specify a valid time in seconds.'

class NoHandlerError(HyperLambdaError):
    """No Handler was specified."""
    fmt = 'You must specify a handler name that need to be called.'

class NoScriptError(HyperLambdaError):
    """No script was specified."""
    fmt = 'You must specify a zip_file or code that need to be executed.'

class NoValidDictionaryError(HyperLambdaError):
    """No script was specified."""
    fmt = """You must specify key-value pairs that represent your environment's configuration settings. eg: "{'Variables': {'string': 'string'} }" """

class NoValidTagsDictionaryError(HyperLambdaError):
    fmt = """You must specify key-value pairs that represent your tags's configuration settings. eg: {'string': 'string'} """

class NoValidDataTypeError(HyperLambdaError):
    fmt = """You must specify a json dictionary that represent your data's configuration settings. """

class InstanceTerminatedError(HyperLambdaError):
    """No script was specified."""
    fmt = "Instance Terminated. '{message}'"

class FunctionTimeoutError(HyperLambdaError):
    """No script was specified."""
    fmt = "Task timed out after '{timeout}'' seconds"

class NoInstanceCreated(HyperLambdaError):
    fmt = "{message}"

class NoFunctionError(HyperLambdaError):
    fmt = "An error occurred when calling the describe_function operation. '{message}'"

class InvalidHandlerError(HyperLambdaError):
    fmt = "The data given is not valid. "    

class InvalidKeyNameTypeError(HyperLambdaError):
    fmt = "KeyName should be of type string"

class InvalidSecurityGroupIdsTypeError(HyperLambdaError):
    fmt = "SecurityGroupIds should be of type list"