# coding: utf-8

"""
    forumsentry_api
    
"""


import pprint
import re  # noqa: F401

import six


class VirtualDirectory(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'acl_policy': 'str',
        'remote_path': 'str',
        'virtual_host': 'str',
        'name': 'str',
        'enabled': 'bool',
        'listener_policy': 'str',
        'description': 'str',
        'request_process_type': 'str',
        'virtual_path': 'str',
        'error_template': 'str',
        'use_remote_policy': 'bool',
        'response_process_type': 'str',
        'remote_policy': 'str',
        'request_process': 'str',
        'request_filter_policy': 'str',
        'response_process': 'str'
    }

    attribute_map = {
        'acl_policy': 'aclPolicy',
        'remote_path': 'remotePath',
        'virtual_host': 'virtualHost',
        'name': 'name',
        'enabled': 'enabled',
        'listener_policy': 'listenerPolicy',
        'description': 'description',
        'request_process_type': 'requestProcessType',
        'virtual_path': 'virtualPath',
        'error_template': 'errorTemplate',
        'use_remote_policy': 'useRemotePolicy',
        'response_process_type': 'responseProcessType',
        'remote_policy': 'remotePolicy',
        'request_process': 'requestProcess',
        'request_filter_policy': 'requestFilterPolicy',
        'response_process': 'responseProcess'
    }

    def __init__(self, acl_policy=None, remote_path=None, virtual_host=None, name=None, enabled=None, listener_policy=None, description=None, request_process_type=None, virtual_path=None, error_template=None, use_remote_policy=None, response_process_type=None, remote_policy=None, request_process=None, request_filter_policy=None, response_process=None):  # noqa: E501
        """VirtualDirectory - a model defined in Swagger"""  # noqa: E501

        self._acl_policy = None
        self._remote_path = None
        self._virtual_host = None
        self._name = None
        self._enabled = None
        self._listener_policy = None
        self._description = None
        self._request_process_type = None
        self._virtual_path = None
        self._error_template = None
        self._use_remote_policy = None
        self._response_process_type = None
        self._remote_policy = None
        self._request_process = None
        self._request_filter_policy = None
        self._response_process = None
        self.discriminator = None

        if acl_policy is not None:
            self._acl_policy = acl_policy
        if remote_path is not None:
            self._remote_path = remote_path
        if virtual_host is not None:
            self._virtual_host = virtual_host
        if name is not None:
            self._name = name
        if enabled is not None:
            self._enabled = enabled
        if listener_policy is not None:
            self._listener_policy = listener_policy
        if description is not None:
            self._description = description
        if request_process_type is not None:
            self._request_process_type = request_process_type
        if virtual_path is not None:
            self._virtual_path = virtual_path
        if error_template is not None:
            self._error_template = error_template
        if use_remote_policy is not None:
            self._use_remote_policy = use_remote_policy
        if response_process_type is not None:
            self._response_process_type = response_process_type
        if remote_policy is not None:
            self._remote_policy = remote_policy
        if request_process is not None:
            self._request_process = request_process
        if request_filter_policy is not None:
            self._request_filter_policy = request_filter_policy
        if response_process is not None:
            self._response_process = response_process

    @property
    def acl_policy(self):
        """Gets the acl_policy of this VirtualDirectory.  # noqa: E501


        :return: The acl_policy of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._acl_policy

    @acl_policy.setter
    def acl_policy(self, acl_policy):
        """Sets the acl_policy of this VirtualDirectory.


        :param acl_policy: The acl_policy of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._acl_policy = acl_policy

    @property
    def remote_path(self):
        """Gets the remote_path of this VirtualDirectory.  # noqa: E501


        :return: The remote_path of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._remote_path

    @remote_path.setter
    def remote_path(self, remote_path):
        """Sets the remote_path of this VirtualDirectory.


        :param remote_path: The remote_path of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._remote_path = remote_path

    @property
    def virtual_host(self):
        """Gets the virtual_host of this VirtualDirectory.  # noqa: E501


        :return: The virtual_host of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._virtual_host

    @virtual_host.setter
    def virtual_host(self, virtual_host):
        """Sets the virtual_host of this VirtualDirectory.


        :param virtual_host: The virtual_host of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._virtual_host = virtual_host

    @property
    def name(self):
        """Gets the name of this VirtualDirectory.  # noqa: E501


        :return: The name of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this VirtualDirectory.


        :param name: The name of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def enabled(self):
        """Gets the enabled of this VirtualDirectory.  # noqa: E501


        :return: The enabled of this VirtualDirectory.  # noqa: E501
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """Sets the enabled of this VirtualDirectory.


        :param enabled: The enabled of this VirtualDirectory.  # noqa: E501
        :type: bool
        """

        self._enabled = enabled

    @property
    def listener_policy(self):
        """Gets the listener_policy of this VirtualDirectory.  # noqa: E501


        :return: The listener_policy of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._listener_policy

    @listener_policy.setter
    def listener_policy(self, listener_policy):
        """Sets the listener_policy of this VirtualDirectory.


        :param listener_policy: The listener_policy of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._listener_policy = listener_policy

    @property
    def description(self):
        """Gets the description of this VirtualDirectory.  # noqa: E501


        :return: The description of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this VirtualDirectory.


        :param description: The description of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def request_process_type(self):
        """Gets the request_process_type of this VirtualDirectory.  # noqa: E501


        :return: The request_process_type of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._request_process_type

    @request_process_type.setter
    def request_process_type(self, request_process_type):
        """Sets the request_process_type of this VirtualDirectory.


        :param request_process_type: The request_process_type of this VirtualDirectory.  # noqa: E501
        :type: str
        """
        allowed_values = ["TASK_LIST", "TASK_LIST_GROUP"]  # noqa: E501
        if request_process_type not in allowed_values:
            raise ValueError(
                "Invalid value for `request_process_type` ({0}), must be one of {1}"  # noqa: E501
                .format(request_process_type, allowed_values)
            )

        self._request_process_type = request_process_type

    @property
    def virtual_path(self):
        """Gets the virtual_path of this VirtualDirectory.  # noqa: E501


        :return: The virtual_path of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._virtual_path

    @virtual_path.setter
    def virtual_path(self, virtual_path):
        """Sets the virtual_path of this VirtualDirectory.


        :param virtual_path: The virtual_path of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._virtual_path = virtual_path

    @property
    def error_template(self):
        """Gets the error_template of this VirtualDirectory.  # noqa: E501


        :return: The error_template of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._error_template

    @error_template.setter
    def error_template(self, error_template):
        """Sets the error_template of this VirtualDirectory.


        :param error_template: The error_template of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._error_template = error_template

    @property
    def use_remote_policy(self):
        """Gets the use_remote_policy of this VirtualDirectory.  # noqa: E501


        :return: The use_remote_policy of this VirtualDirectory.  # noqa: E501
        :rtype: bool
        """
        return self._use_remote_policy

    @use_remote_policy.setter
    def use_remote_policy(self, use_remote_policy):
        """Sets the use_remote_policy of this VirtualDirectory.


        :param use_remote_policy: The use_remote_policy of this VirtualDirectory.  # noqa: E501
        :type: bool
        """

        self._use_remote_policy = use_remote_policy

    @property
    def response_process_type(self):
        """Gets the response_process_type of this VirtualDirectory.  # noqa: E501


        :return: The response_process_type of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._response_process_type

    @response_process_type.setter
    def response_process_type(self, response_process_type):
        """Sets the response_process_type of this VirtualDirectory.


        :param response_process_type: The response_process_type of this VirtualDirectory.  # noqa: E501
        :type: str
        """
        allowed_values = ["TASK_LIST", "TASK_LIST_GROUP"]  # noqa: E501
        if response_process_type not in allowed_values:
            raise ValueError(
                "Invalid value for `response_process_type` ({0}), must be one of {1}"  # noqa: E501
                .format(response_process_type, allowed_values)
            )

        self._response_process_type = response_process_type

    @property
    def remote_policy(self):
        """Gets the remote_policy of this VirtualDirectory.  # noqa: E501


        :return: The remote_policy of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._remote_policy

    @remote_policy.setter
    def remote_policy(self, remote_policy):
        """Sets the remote_policy of this VirtualDirectory.


        :param remote_policy: The remote_policy of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._remote_policy = remote_policy

    @property
    def request_process(self):
        """Gets the request_process of this VirtualDirectory.  # noqa: E501


        :return: The request_process of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._request_process

    @request_process.setter
    def request_process(self, request_process):
        """Sets the request_process of this VirtualDirectory.


        :param request_process: The request_process of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._request_process = request_process

    @property
    def request_filter_policy(self):
        """Gets the request_filter_policy of this VirtualDirectory.  # noqa: E501


        :return: The request_filter_policy of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._request_filter_policy

    @request_filter_policy.setter
    def request_filter_policy(self, request_filter_policy):
        """Sets the request_filter_policy of this VirtualDirectory.


        :param request_filter_policy: The request_filter_policy of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._request_filter_policy = request_filter_policy

    @property
    def response_process(self):
        """Gets the response_process of this VirtualDirectory.  # noqa: E501


        :return: The response_process of this VirtualDirectory.  # noqa: E501
        :rtype: str
        """
        return self._response_process

    @response_process.setter
    def response_process(self, response_process):
        """Sets the response_process of this VirtualDirectory.


        :param response_process: The response_process of this VirtualDirectory.  # noqa: E501
        :type: str
        """

        self._response_process = response_process

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, VirtualDirectory):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
