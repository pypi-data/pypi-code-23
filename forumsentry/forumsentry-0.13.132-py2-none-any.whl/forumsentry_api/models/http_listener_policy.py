# coding: utf-8

"""
    forumsentry_api
    
"""


import pprint
import re  # noqa: F401

import six


class HttpListenerPolicy(object):
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
        'use_cookie_authentication': 'bool',
        'use_basic_authentication': 'bool',
        'acl_policy': 'str',
        'ip_acl_policy': 'str',
        'read_timeout_millis': 'int',
        'password_parameter': 'str',
        'use_digest_authentication': 'bool',
        'use_chunking': 'bool',
        'port': 'int',
        'use_device_ip': 'bool',
        'name': 'str',
        'description': 'str',
        'use_form_post_authentication': 'bool',
        'listener_ssl_policy': 'str',
        'username_parameter': 'str',
        'enabled': 'bool',
        'interface': 'str',
        'error_template': 'str',
        'listener_host': 'str',
        'listener_ssl_enabled': 'bool',
        'password_authentication_realm': 'str',
        'require_password_authentication': 'bool',
        'use_kerberos_authentication': 'bool'
    }

    attribute_map = {
        'use_cookie_authentication': 'useCookieAuthentication',
        'use_basic_authentication': 'useBasicAuthentication',
        'acl_policy': 'aclPolicy',
        'ip_acl_policy': 'ipAclPolicy',
        'read_timeout_millis': 'readTimeoutMillis',
        'password_parameter': 'passwordParameter',
        'use_digest_authentication': 'useDigestAuthentication',
        'use_chunking': 'useChunking',
        'port': 'port',
        'use_device_ip': 'useDeviceIp',
        'name': 'name',
        'description': 'description',
        'use_form_post_authentication': 'useFormPostAuthentication',
        'listener_ssl_policy': 'listenerSSLPolicy',
        'username_parameter': 'usernameParameter',
        'enabled': 'enabled',
        'interface': 'interface',
        'error_template': 'errorTemplate',
        'listener_host': 'listenerHost',
        'listener_ssl_enabled': 'listenerSSLEnabled',
        'password_authentication_realm': 'passwordAuthenticationRealm',
        'require_password_authentication': 'requirePasswordAuthentication',
        'use_kerberos_authentication': 'useKerberosAuthentication'
    }

    def __init__(self, use_cookie_authentication=None, use_basic_authentication=None, acl_policy=None, ip_acl_policy=None, read_timeout_millis=None, password_parameter=None, use_digest_authentication=None, use_chunking=None, port=None, use_device_ip=None, name=None, description=None, use_form_post_authentication=None, listener_ssl_policy=None, username_parameter=None, enabled=None, interface=None, error_template=None, listener_host=None, listener_ssl_enabled=None, password_authentication_realm=None, require_password_authentication=None, use_kerberos_authentication=None):  # noqa: E501
        """HttpListenerPolicy - a model defined in Swagger"""  # noqa: E501

        self._use_cookie_authentication = None
        self._use_basic_authentication = None
        self._acl_policy = None
        self._ip_acl_policy = None
        self._read_timeout_millis = None
        self._password_parameter = None
        self._use_digest_authentication = None
        self._use_chunking = None
        self._port = None
        self._use_device_ip = None
        self._name = None
        self._description = None
        self._use_form_post_authentication = None
        self._listener_ssl_policy = None
        self._username_parameter = None
        self._enabled = None
        self._interface = None
        self._error_template = None
        self._listener_host = None
        self._listener_ssl_enabled = None
        self._password_authentication_realm = None
        self._require_password_authentication = None
        self._use_kerberos_authentication = None
        self.discriminator = None

        if use_cookie_authentication is not None:
            self._use_cookie_authentication = use_cookie_authentication
        if use_basic_authentication is not None:
            self._use_basic_authentication = use_basic_authentication
        if acl_policy is not None:
            self._acl_policy = acl_policy
        if ip_acl_policy is not None:
            self._ip_acl_policy = ip_acl_policy
        if read_timeout_millis is not None:
            self._read_timeout_millis = read_timeout_millis
        if password_parameter is not None:
            self._password_parameter = password_parameter
        if use_digest_authentication is not None:
            self._use_digest_authentication = use_digest_authentication
        if use_chunking is not None:
            self._use_chunking = use_chunking
        if port is not None:
            self._port = port
        if use_device_ip is not None:
            self._use_device_ip = use_device_ip
        if name is not None:
            self._name = name
        if description is not None:
            self._description = description
        if use_form_post_authentication is not None:
            self._use_form_post_authentication = use_form_post_authentication
        if listener_ssl_policy is not None:
            self._listener_ssl_policy = listener_ssl_policy
        if username_parameter is not None:
            self._username_parameter = username_parameter
        if enabled is not None:
            self._enabled = enabled
        if interface is not None:
            self._interface = interface
        if error_template is not None:
            self._error_template = error_template
        if listener_host is not None:
            self._listener_host = listener_host
        if listener_ssl_enabled is not None:
            self._listener_ssl_enabled = listener_ssl_enabled
        if password_authentication_realm is not None:
            self._password_authentication_realm = password_authentication_realm
        if require_password_authentication is not None:
            self._require_password_authentication = require_password_authentication
        if use_kerberos_authentication is not None:
            self._use_kerberos_authentication = use_kerberos_authentication

    @property
    def use_cookie_authentication(self):
        """Gets the use_cookie_authentication of this HttpListenerPolicy.  # noqa: E501


        :return: The use_cookie_authentication of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._use_cookie_authentication

    @use_cookie_authentication.setter
    def use_cookie_authentication(self, use_cookie_authentication):
        """Sets the use_cookie_authentication of this HttpListenerPolicy.


        :param use_cookie_authentication: The use_cookie_authentication of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._use_cookie_authentication = use_cookie_authentication

    @property
    def use_basic_authentication(self):
        """Gets the use_basic_authentication of this HttpListenerPolicy.  # noqa: E501


        :return: The use_basic_authentication of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._use_basic_authentication

    @use_basic_authentication.setter
    def use_basic_authentication(self, use_basic_authentication):
        """Sets the use_basic_authentication of this HttpListenerPolicy.


        :param use_basic_authentication: The use_basic_authentication of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._use_basic_authentication = use_basic_authentication

    @property
    def acl_policy(self):
        """Gets the acl_policy of this HttpListenerPolicy.  # noqa: E501


        :return: The acl_policy of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._acl_policy

    @acl_policy.setter
    def acl_policy(self, acl_policy):
        """Sets the acl_policy of this HttpListenerPolicy.


        :param acl_policy: The acl_policy of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._acl_policy = acl_policy

    @property
    def ip_acl_policy(self):
        """Gets the ip_acl_policy of this HttpListenerPolicy.  # noqa: E501


        :return: The ip_acl_policy of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._ip_acl_policy

    @ip_acl_policy.setter
    def ip_acl_policy(self, ip_acl_policy):
        """Sets the ip_acl_policy of this HttpListenerPolicy.


        :param ip_acl_policy: The ip_acl_policy of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._ip_acl_policy = ip_acl_policy

    @property
    def read_timeout_millis(self):
        """Gets the read_timeout_millis of this HttpListenerPolicy.  # noqa: E501


        :return: The read_timeout_millis of this HttpListenerPolicy.  # noqa: E501
        :rtype: int
        """
        return self._read_timeout_millis

    @read_timeout_millis.setter
    def read_timeout_millis(self, read_timeout_millis):
        """Sets the read_timeout_millis of this HttpListenerPolicy.


        :param read_timeout_millis: The read_timeout_millis of this HttpListenerPolicy.  # noqa: E501
        :type: int
        """

        self._read_timeout_millis = read_timeout_millis

    @property
    def password_parameter(self):
        """Gets the password_parameter of this HttpListenerPolicy.  # noqa: E501


        :return: The password_parameter of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._password_parameter

    @password_parameter.setter
    def password_parameter(self, password_parameter):
        """Sets the password_parameter of this HttpListenerPolicy.


        :param password_parameter: The password_parameter of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._password_parameter = password_parameter

    @property
    def use_digest_authentication(self):
        """Gets the use_digest_authentication of this HttpListenerPolicy.  # noqa: E501


        :return: The use_digest_authentication of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._use_digest_authentication

    @use_digest_authentication.setter
    def use_digest_authentication(self, use_digest_authentication):
        """Sets the use_digest_authentication of this HttpListenerPolicy.


        :param use_digest_authentication: The use_digest_authentication of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._use_digest_authentication = use_digest_authentication

    @property
    def use_chunking(self):
        """Gets the use_chunking of this HttpListenerPolicy.  # noqa: E501


        :return: The use_chunking of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._use_chunking

    @use_chunking.setter
    def use_chunking(self, use_chunking):
        """Sets the use_chunking of this HttpListenerPolicy.


        :param use_chunking: The use_chunking of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._use_chunking = use_chunking

    @property
    def port(self):
        """Gets the port of this HttpListenerPolicy.  # noqa: E501


        :return: The port of this HttpListenerPolicy.  # noqa: E501
        :rtype: int
        """
        return self._port

    @port.setter
    def port(self, port):
        """Sets the port of this HttpListenerPolicy.


        :param port: The port of this HttpListenerPolicy.  # noqa: E501
        :type: int
        """

        self._port = port

    @property
    def use_device_ip(self):
        """Gets the use_device_ip of this HttpListenerPolicy.  # noqa: E501


        :return: The use_device_ip of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._use_device_ip

    @use_device_ip.setter
    def use_device_ip(self, use_device_ip):
        """Sets the use_device_ip of this HttpListenerPolicy.


        :param use_device_ip: The use_device_ip of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._use_device_ip = use_device_ip

    @property
    def name(self):
        """Gets the name of this HttpListenerPolicy.  # noqa: E501


        :return: The name of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this HttpListenerPolicy.


        :param name: The name of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def description(self):
        """Gets the description of this HttpListenerPolicy.  # noqa: E501


        :return: The description of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this HttpListenerPolicy.


        :param description: The description of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def use_form_post_authentication(self):
        """Gets the use_form_post_authentication of this HttpListenerPolicy.  # noqa: E501


        :return: The use_form_post_authentication of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._use_form_post_authentication

    @use_form_post_authentication.setter
    def use_form_post_authentication(self, use_form_post_authentication):
        """Sets the use_form_post_authentication of this HttpListenerPolicy.


        :param use_form_post_authentication: The use_form_post_authentication of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._use_form_post_authentication = use_form_post_authentication

    @property
    def listener_ssl_policy(self):
        """Gets the listener_ssl_policy of this HttpListenerPolicy.  # noqa: E501


        :return: The listener_ssl_policy of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._listener_ssl_policy

    @listener_ssl_policy.setter
    def listener_ssl_policy(self, listener_ssl_policy):
        """Sets the listener_ssl_policy of this HttpListenerPolicy.


        :param listener_ssl_policy: The listener_ssl_policy of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._listener_ssl_policy = listener_ssl_policy

    @property
    def username_parameter(self):
        """Gets the username_parameter of this HttpListenerPolicy.  # noqa: E501


        :return: The username_parameter of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._username_parameter

    @username_parameter.setter
    def username_parameter(self, username_parameter):
        """Sets the username_parameter of this HttpListenerPolicy.


        :param username_parameter: The username_parameter of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._username_parameter = username_parameter

    @property
    def enabled(self):
        """Gets the enabled of this HttpListenerPolicy.  # noqa: E501


        :return: The enabled of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """Sets the enabled of this HttpListenerPolicy.


        :param enabled: The enabled of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._enabled = enabled

    @property
    def interface(self):
        """Gets the interface of this HttpListenerPolicy.  # noqa: E501


        :return: The interface of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._interface

    @interface.setter
    def interface(self, interface):
        """Sets the interface of this HttpListenerPolicy.


        :param interface: The interface of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """
        allowed_values = ["WAN", "LAN"]  # noqa: E501
        if interface not in allowed_values:
            raise ValueError(
                "Invalid value for `interface` ({0}), must be one of {1}"  # noqa: E501
                .format(interface, allowed_values)
            )

        self._interface = interface

    @property
    def error_template(self):
        """Gets the error_template of this HttpListenerPolicy.  # noqa: E501


        :return: The error_template of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._error_template

    @error_template.setter
    def error_template(self, error_template):
        """Sets the error_template of this HttpListenerPolicy.


        :param error_template: The error_template of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._error_template = error_template

    @property
    def listener_host(self):
        """Gets the listener_host of this HttpListenerPolicy.  # noqa: E501


        :return: The listener_host of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._listener_host

    @listener_host.setter
    def listener_host(self, listener_host):
        """Sets the listener_host of this HttpListenerPolicy.


        :param listener_host: The listener_host of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._listener_host = listener_host

    @property
    def listener_ssl_enabled(self):
        """Gets the listener_ssl_enabled of this HttpListenerPolicy.  # noqa: E501


        :return: The listener_ssl_enabled of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._listener_ssl_enabled

    @listener_ssl_enabled.setter
    def listener_ssl_enabled(self, listener_ssl_enabled):
        """Sets the listener_ssl_enabled of this HttpListenerPolicy.


        :param listener_ssl_enabled: The listener_ssl_enabled of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._listener_ssl_enabled = listener_ssl_enabled

    @property
    def password_authentication_realm(self):
        """Gets the password_authentication_realm of this HttpListenerPolicy.  # noqa: E501


        :return: The password_authentication_realm of this HttpListenerPolicy.  # noqa: E501
        :rtype: str
        """
        return self._password_authentication_realm

    @password_authentication_realm.setter
    def password_authentication_realm(self, password_authentication_realm):
        """Sets the password_authentication_realm of this HttpListenerPolicy.


        :param password_authentication_realm: The password_authentication_realm of this HttpListenerPolicy.  # noqa: E501
        :type: str
        """

        self._password_authentication_realm = password_authentication_realm

    @property
    def require_password_authentication(self):
        """Gets the require_password_authentication of this HttpListenerPolicy.  # noqa: E501


        :return: The require_password_authentication of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._require_password_authentication

    @require_password_authentication.setter
    def require_password_authentication(self, require_password_authentication):
        """Sets the require_password_authentication of this HttpListenerPolicy.


        :param require_password_authentication: The require_password_authentication of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._require_password_authentication = require_password_authentication

    @property
    def use_kerberos_authentication(self):
        """Gets the use_kerberos_authentication of this HttpListenerPolicy.  # noqa: E501


        :return: The use_kerberos_authentication of this HttpListenerPolicy.  # noqa: E501
        :rtype: bool
        """
        return self._use_kerberos_authentication

    @use_kerberos_authentication.setter
    def use_kerberos_authentication(self, use_kerberos_authentication):
        """Sets the use_kerberos_authentication of this HttpListenerPolicy.


        :param use_kerberos_authentication: The use_kerberos_authentication of this HttpListenerPolicy.  # noqa: E501
        :type: bool
        """

        self._use_kerberos_authentication = use_kerberos_authentication

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
        if not isinstance(other, HttpListenerPolicy):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
