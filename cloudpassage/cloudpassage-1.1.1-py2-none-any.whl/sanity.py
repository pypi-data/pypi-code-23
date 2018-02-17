"""Collection of functions for doing validation and sanity checking"""

import os
import re
from cloudpassage.exceptions import CloudPassageValidation


def validate_object_id(object_id):
    """Validates object ID (server_id, policy_id, etc...)

    This function validates Object IDs with the intent of guarding against \
    URL traversal.

    Args:
        object_id (str or list): Object ID to be validated

    Returns:
        (bool) True if valid, throws an exception otherwise.

    """

    rex = re.compile('^[A-Za-z0-9]+$')
    if isinstance(object_id, (str, unicode)):
        if not rex.match(object_id):
            error_message = "Object ID failed validation: %s" % object_id
            raise CloudPassageValidation(error_message)
        else:
            return True
    elif isinstance(object_id, list):
        for individual in object_id:
            if not rex.match(individual):
                error_message = "Object ID failed validation: %s" % object_id
                raise CloudPassageValidation(error_message)
        return True
    else:
        error_message = "Wrong type for object ID: %s" % str(type(object_id))
        raise TypeError(error_message)


def validate_api_hostname(api_hostname):
    """Validate hostname for API endpoint"""
    hostname_is_valid = False
    valid_api_host = re.compile(r'^([A-Za-z0-9-]+\.){1,2}cloudpassage\.com$')
    if valid_api_host.match(api_hostname):
        hostname_is_valid = True
    return hostname_is_valid


def validate_config_path(config_path):
    """Validate config file path exists"""
    if os.path.exists(config_path):
        return True


def validate_cve_exception_scope_id(scope_id):
    """Validate CVE Exception create request body"""
    if re.findall('[^A-Za-z0-9]', scope_id):
        error_message = "Please make sure to provide a \
        valid scope id."
        raise CloudPassageValidation(error_message)
    return True
