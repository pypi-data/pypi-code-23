#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ironpipe Extension API Python library

The Ironpipe extension library provides a number of helper functions that simplify
creating ironpipe extension modules. Extensions do not need to use the Ironpipe library.

get_resource(arg=None)
	A dictionary containing the parsed name / value pairs of the --resource
    argument.

get_config(arg=None)
    A dictionary containg the parsed name / value pairs of the 'config'
    part of the --resource element, or parsed value of the --config argument

get_metadata(arg=None)
    Returns dictionary containing the name/value pairs of any metadata
    associated with input stream. This function is a shortcut for
    parsing $IRONPIPE_INPUT_METADATA.

set_metadata(name, value)
    Update the metadata for any data written to the output stream. This
    function is a shortcut for writing a JSON string into
    `$IRONPIPE_OUTPUT_METADATA`.

log(level, message)
    Log message to 'stderr' with severity 'level`. Level needs to be one of
    `error`, `warning`, `info`, `success-audit`, `failure-audit`, `debug`.
    The levels `success-audit` and `failure-audit` log audited security events.
    For example, a user's successful attempt to log on to the system is logged
    as a `success-audit` event, while a failed attempt to log into a database is
    logged as a `failure-audit` event.

exit([message])
    Terminate execution either successfully (return 0 or no argument) or
    log error with 'message' and exit with none-zero status.This function
    is a shortcut for writing 'message' to stderr and then calling the
    exit() function with either a SUCCESS or FAILURE status.
"""

import sys
import os
import json
import argparse
import yaml

# Define system contants
RESOURCE_ARG_STRING = '--resource'
RESOURCE_ARG_SHORT_STRING = '-r'
CONFIG_ARG_STRING = '--config'
CONFIG_ARG_SHORT_STRING = '-c'
DEBUG_ARG_STRING = '--debug'
DEBUG_ARG_SHORT_STRING = '-d'
IRONPIPE_INPUT_METADATA = 'IRONPIPE_INPUT_METADATA'
IRONPIPE_OUTPUT_METADATA = 'IRONPIPE_OUTPUT_METADATA'

DEBUG_MODE = False

#
#
def _parse_args():
    '''
    '''
    parser = argparse.ArgumentParser(description='Run Ironpipe Extension.')
    parser.add_argument(RESOURCE_ARG_STRING, RESOURCE_ARG_SHORT_STRING,
                        default=None, help='resource declaration JSON or YAML file')
    parser.add_argument(CONFIG_ARG_STRING, CONFIG_ARG_SHORT_STRING,
                        default=None, help='config declaration JSON or YAML file')
    parser.add_argument(DEBUG_ARG_STRING, DEBUG_ARG_SHORT_STRING, action='store_true',
                        help='turn on debug logging')
    args = parser.parse_args()

    resource_arg = args.resource
    config_arg = args.config
    debug_arg = args.debug

    resource = None
    config = None

    # Try to parse passed JSON strings
    if resource_arg:
        try:
            resource = json.loads(resource_arg)
        except:
            # Check if the argument might have been a file path
            if not resource and os.path.isfile(resource_arg):
                with open(resource_arg, 'r') as f:
                    try:
                        resource = yaml.load(f)
                    except yaml.YAMLError as err:
                        exit("Unable to parse resource declaration file '{}': {}".format(resource_arg, err))
            else:
                exit('--resource argument must be JSON string or file')

    if config_arg:
        try:
            config = json.loads(config_arg)
        except:
            # Check if the argument might have been a file path
            if not config and os.path.isfile(config_arg):
                with open(config_arg, 'r') as f:
                    try:
                        config = yaml.load(f)
                    except yaml.YAMLError as err:
                        exit("Unable to parse config declaration file '{}': {}".format(config_arg, err))
            else:
                exit('--config argument must be JSON string or file')

    # If both resource and config are defined, config overrides resource
    if resource and config:
        resource['config'] = config
    # else if only resource is defined, extract 'config' arguments
    elif resource:
        config = resource.get('config')

    # Log debug messages
    if debug_arg:
        global DEBUG_MODE
        DEBUG_MODE = True

    return resource, config

#
#
def get_resource(arg=None):
    '''
    returns: Either a dictionary containing the parsed name / value pairs of
        the --resource argument or the value of 'arg'. Returns None if no
        argument was passed or the JSON could not be parsed.
    '''
    resource, config = _parse_args()

    if resource and arg:
        return resource.get(arg)
    else:
        return resource

#
#
def get_config(arg=None):
    '''
    <arg>:
    returns: Either a dictionary containing the parsed name / value pairs of
        the 'config' dictionary argument or the value of 'arg'. Returns
        None if no argument was passed or the JSON could not be parsed.
    '''
    resource, config = _parse_args()

    if config and arg:
        return config.get(arg)
    else:
        return config

#
#
def _read_metadata_from_variable(variable):
    '''
    Helper function that parses JSON string from environ variable 'variable'
    '''
    metadata = os.environ.get(variable)

    if metadata:
        try:
            metadata = json.loads(metadata)
        except:
            metadata = None

    return metadata

#
#
def get_metadata(arg=None):
    '''
    Returns either a dictionary containing the name/value pairs of any metadata
    associated with the input stream or the value of 'arg'. This function is a
    shortcut for parsing `$IRONPIPE_INPUT_METADATA`. Returns None if the
    variable has not been set the JSON string could not be parsed.
    '''
    metadata = _read_metadata_from_variable(IRONPIPE_INPUT_METADATA)

    # if a arg was specified, return the value of arg
    if metadata and arg:
        metadata = metadata.get(arg)

    return metadata

#
#
def set_metadata(name, value):
    '''
    Update the metadata for any data written to the output stream. This
    function is a shortcut for writing a JSON string into
    `$IRONPIPE_OUTPUT_METADATA`.
    '''
    metadata = _read_metadata_from_variable(IRONPIPE_OUTPUT_METADATA)

    if metadata is None:
        metadata = {}

    # Add new attribute or update value
    metadata[name] = value

    # Write update metadata values back into environ variable as JSON string
    metadata_json = json.dumps(metadata)
    os.environ[IRONPIPE_OUTPUT_METADATA] = metadata_json

    return metadata

#
# Define log levels
#
ERROR = 'error'
WARNING = 'warning'
INFO = 'info'
DEBUG = 'debug'
SUCCESS_AUDIT = 'success-audit'
FAILURE_AUDIT = 'failure-audit'
LOG_LEVELS = [ERROR, WARNING, INFO, DEBUG, SUCCESS_AUDIT, FAILURE_AUDIT]

#
#
def log(level, message):
    '''
    Log message to 'stderr' with severity 'level`. Level needs to be one of
    `error`, `warning`, `info`, `success-audit`, `failure-audit`, `debug`.
    The levels `success-audit` and `failure-audit` log audited security events.
    For example, a user's successful attempt to log on to the system is logged
    as a `success-audit` event, while a failed attempt to log into a database is
    logged as a `failure-audit` event.
    '''
    global DEBUG_MODE
    # Skip logging debug messages unless DEBUG_MODE is set
    if level == DEBUG and not DEBUG_MODE:
        return

    # Make sure level is valid
    if not level or not isinstance(level, str) or level.lower() not in LOG_LEVELS:
        levels = ', '.join([i for i in LOG_LEVELS])
        log(ERROR, 'log level must be one of: {}'.format(levels))
        return

    sys.stderr.write('[{}] {}'.format(level, message))

#
#
def exit(message=None):
    '''
    Terminate execution either successfully (return 0 or no argument) or with
    `error error_message`. This function is a shortcut for writing
    `error_message` to `stderr` and then calling the `exit()` function with
    either a `SUCCESS` or `FAILURE` status.
    '''
    if message:
        log(ERROR, message)
        sys.exit(1)
    else:
        sys.exit(0)
