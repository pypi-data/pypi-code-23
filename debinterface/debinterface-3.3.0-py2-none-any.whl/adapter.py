# -*- coding: utf-8 -*-
"""The NetworkAdapter class represents an interface and its configuration
from the /etc/network/interfaces.
It tries to validate data before writting, but it is by no means fool proof.
It has setter for many common options, but it is impossible to have setter for
every options on earth !
"""
from __future__ import print_function, with_statement, absolute_import
import socket
import warnings
from .adapterValidation import NetworkAdapterValidation, VALID_OPTS


class NetworkAdapter(object):
    """ A representation a network adapter. """

    @property
    def attributes(self):
        return self._ifAttributes

    def get_attr(self, attr):
        return self._ifAttributes[attr]

    def validateAll(self):
        """ Not thorough validations... and quick coded.

            Raises:
                ValueError: if there is a validation error
        """
        self._validator.validate_all(self._ifAttributes)

    def validateOne(self, opt, validations, val):
        """ Not thorough validations... and quick coded.

            Args:
                opt (str): key name of the option
                validations (dict): contains the validations to checks
                val (any): the option value

            Raises:
                ValueError: if there is a validation error
        """
        self._validator.validate_one(opt, validations, val)

    @staticmethod
    def validateIP(ip):
        """Validate an IP Address. Works for subnet masks too.

            Args:
                ip (str): the IP as a string

            Raises:
                socket.error on invalid IP
        """
        try:
            socket.inet_aton(ip)
        except socket.error:
            socket.inet_pton(socket.AF_INET6, ip)

    def setName(self, name):
        """Set the name option of an interface.

            Args:
                name (str): the name of the interface

            Raises:
                ValueError: if there is a validation error
        """
        self._validator.validate_one('name', VALID_OPTS['name'], name)
        self._ifAttributes['name'] = str(name)

    def setAddrFam(self, address_family):
        """ Set the address family option of an interface.

            Args:
                address_family (str): one of 'inet', 'inet6', 'ipx'

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'addrFam', VALID_OPTS['addrFam'], address_family)
        self._ifAttributes['addrFam'] = address_family

    def setAddressSource(self, address_source):
        """ Set the address source for an interface.

        Valid values are : dhcp, static, loopback, manual,
        bootp, ppp, wvdial, dynamic, ipv4ll, v4tunnel

            Args:
                address_source (string): address source for an interface

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'source', VALID_OPTS['source'], address_source)
        self._ifAttributes['source'] = address_source

    def setAddress(self, ip_address):
        """ Set the ipaddress of an interface.

            Args:
                ip_address (str): the IP as a string

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'address', VALID_OPTS['address'], ip_address)
        self._ifAttributes['address'] = ip_address

    def setNetmask(self, netmask):
        """ Set the netmask of an interface.

            Args:
                netmask (str): the netmask IP as a string

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'netmask', VALID_OPTS['netmask'], netmask)
        self._ifAttributes['netmask'] = netmask

    def setGateway(self, gateway):
        """ Set the default gateway of an interface.

            Args:
                gateway (str): the gateway IP as a string

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'gateway', VALID_OPTS['gateway'], gateway)
        self._ifAttributes['gateway'] = gateway

    def setBroadcast(self, broadcast):
        """ Set the broadcast address of an interface.

            Args:
                broadcast (str): the broadcast IP as a string

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'broadcast', VALID_OPTS['broadcast'], broadcast)
        self._ifAttributes['broadcast'] = broadcast

    def setNetwork(self, network):
        """ Set the network identifier of an interface.

            Args:
                network (str): the IP as a string

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'network', VALID_OPTS['network'], network)
        self._ifAttributes['network'] = network

    def setAuto(self, auto):
        """ Set the option to autostart the interface.

            Args:
                auto (bool): interface will be set as auto if True

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'auto', VALID_OPTS['auto'], auto)
        self._ifAttributes['auto'] = auto

    def setHotplug(self, hotplug):
        """ Set the option to allow hotplug on the interface.
        Beware, option is really called allow-hotplug, that's a
        small historic cruft...

            Args:
                hotplug (bool): interface hotplug will be set if True

            Raises:
                ValueError: if there is a validation error
        """

        msg = "hotplug key will be renamed into allow-hotplug in 4.0"
        warnings.warn(msg, DeprecationWarning)

        self._validator.validate_one(
            'hotplug', VALID_OPTS['hotplug'], hotplug)
        self._ifAttributes['hotplug'] = hotplug

    def setHostapd(self, hostapd):
        """ Set the wifi conf file on the interface.

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'hostapd', VALID_OPTS['hostapd'], hostapd)
        self._ifAttributes['hostapd'] = hostapd

    def setDnsNameservers(self, nameservers):
        """ Set the dns nameservers on the interface.

            Args:
                nameservers (str): the IP as a string

            Raises:
                ValueError: if there is a validation error
        """

        self._validator.validate_one(
            'dns-nameservers', VALID_OPTS['dns-nameservers'], nameservers)
        self._ifAttributes['dns-nameservers'] = nameservers

    def setDnsSearch(self, searchUri):
        """ Set the dns default search URI.

            Args:
                searchURI (str): The default search domain

            Raises:
                ValueError: if there is a validation error
        """
        self._validator.validate_one(
            'dns-search', VALID_OPTS['dns-search'], searchUri)
        self._ifAttributes['dns-search'] = searchUri

    def setBropts(self, opts):
        """Set the bridge options of an interface.

            Args:
                opts (dict): a dictionary mapping option names and values.
                    In the interfaces file, options will have a bridge prefix.

            Raises:
                ValueError: if there is a validation error

        """

        self._validator.validate_one(
            'bridge-opts', VALID_OPTS['bridge-opts'], opts)
        self._ifAttributes['bridge-opts'] = opts

    def setWpaConf(self, conf_path):
        '''Set the wpa supplicant configuration path for supplicant
        config for wireless interfaces.

        Args:
            conf_path (str): Path at which the supplicant config is located.
        '''
        self._ifAttributes['wpa-conf'] = conf_path

    def replaceBropt(self, key, value):
        """Set a discrete bridge option key with value

            Args:
                key (str): the option key in the bridge option
                value (any): the value
        """

        self._ifAttributes['bridge-opts'][key] = value

    def appendBropts(self, key, value):
        """Set a discrete bridge option key with value

            Args:
                key (str): the option key in the bridge option
                value (any): the value
        """
        new_value = value
        if key in self._ifAttributes['bridge-opts']:
            new_value = self._ifAttributes['bridge-opts'][key] + value
        self.replaceBropt(key, new_value)

    def setUp(self, up):
        """Set and add to the up commands for an interface.

            Args:
                up (list): list of shell commands
        """
        if isinstance(up, list):
            self._ifAttributes['up'] = up
        else:
            self._ifAttributes['up'] = [up]

    def appendUp(self, cmd):
        """Append a shell command to run when the interface is up.

            Args:
                cmd (str): a shell command
        """
        self._ensure_list(self._ifAttributes, "up", cmd)

    def setDown(self, down):
        """Set and add to the down commands for an interface.

            Args:
                down (list): list of shell commands
        """
        if isinstance(down, list):
            self._ifAttributes['down'] = down
        else:
            self._ifAttributes['down'] = [down]

    def appendDown(self, cmd):
        """Append a shell command to run when the interface is down.

            Args:
                cmd (str): a shell command
        """
        self._ensure_list(self._ifAttributes, "down", cmd)

    def setPreUp(self, pre):
        """Set and add to the pre-up commands for an interface.

            Args:
                pre (list): list of shell commands
        """
        if isinstance(pre, list):
            self._ifAttributes['pre-up'] = pre
        else:
            self._ifAttributes['pre-up'] = [pre]

    def appendPreUp(self, cmd):
        """Append a shell command to run when the interface is pre-up.

            Args:
                cmd (str): a shell command
        """
        self._ensure_list(self._ifAttributes, "pre-up", cmd)

    def setPreDown(self, pre):
        """Set and add to the pre-down commands for an interface.

            Args:
                pre (list): list of shell commands
        """
        if isinstance(pre, list):
            self._ifAttributes['pre-down'] = pre
        else:
            self._ifAttributes['pre-down'] = [pre]

    def appendPreDown(self, cmd):
        """Append a shell command to run when the interface is pre-down.

            Args:
                cmd (str): a shell command
        """
        self._ensure_list(self._ifAttributes, "pre-down", cmd)

    def setPostDown(self, post):
        """Set and add to the post-down commands for an interface.

            Args:
                post (list): list of shell commands
        """
        self._ifAttributes['post-down'] = post

    def appendPostDown(self, cmd):
        """Append a shell command to run when the interface is pre-down.

            Args:
                cmd (str): a shell command
        """
        self._ensure_list(self._ifAttributes, "post-down", cmd)

    def setUnknown(self, key, val):
        """Stores uncommon options as there are with no special handling
        It's impossible to know about all available options

            Args:
                key (str): the option name
                val (any): the option value
        """
        if 'unknown' not in self._ifAttributes:
            self._ifAttributes['unknown'] = {}
        self._ifAttributes['unknown'][key] = val

    def export(self, options_list=None):
        """ Return the ifAttributes data structure. as dict.
        You may pass a list of options you want

            Args:
                options_list (list, optional): a list of options you want

            Returns:
                dict: the ifAttributes data structure, optionaly filtered
        """

        if options_list:
            ret = {}
            for k in options_list:
                try:
                    ret[k] = self._ifAttributes[k]
                except KeyError:
                    ret[k] = None
            return ret
        else:
            return self._ifAttributes

    def display(self):
        """Display a (kind of) human readable representation of the adapter."""
        print('============')
        for key, value in self._ifAttributes.items():
            if isinstance(value, list):
                print(key + ': ')
                for item in value:
                    print('\t' + item)
            elif isinstance(value, dict):
                print(key + ': ')
                for item in value.keys():
                    print('\t' + item + ': ' + value[item])
            else:
                print(key + ': ' + str(value))
        print('============')

    def __init__(self, options=None):
        # Initialize attribute storage structre.
        self._validator = NetworkAdapterValidation()
        self._valid = VALID_OPTS  # For backward compatibility
        self.reset()
        self.set_options(options)

    def reset(self):
        """ Initialize attribute storage structure. """
        self._ifAttributes = {}
        self._ifAttributes['bridge-opts'] = {}
        self._ifAttributes['up'] = []
        self._ifAttributes['down'] = []
        self._ifAttributes['pre-up'] = []
        self._ifAttributes['pre-down'] = []
        self._ifAttributes['post-up'] = []
        self._ifAttributes['post-down'] = []

    def set_options(self, options):
        """Set options, either only the name if options is a str,
        or all given options if options is a dict

            Args:
                options (str/dict): historical code... only set
                    the name if options is a str, or all given
                    options if options is a dict

            Raises:
                ValueError: if validation error
                socket.error: if validation error of an IP
                Exception: if anything weird happens
        """

        # Set the name of the interface.
        if isinstance(options, str):
            self.setName(options)

        # If a dictionary of options is provided, populate the adapter options.
        elif isinstance(options, dict):
            try:
                roseta = {
                    'name': self.setName,
                    'addrFam': self.setAddrFam,
                    'source': self.setAddressSource,
                    'address': self.setAddress,
                    'netmask': self.setNetmask,
                    'gateway': self.setGateway,
                    'broadcast': self.setBroadcast,
                    'network': self.setNetwork,
                    'auto': self.setAuto,
                    'allow-hotplug': self.setHotplug,
                    'hotplug': self.setHotplug,
                    'bridgeOpts': self.setBropts,
                    'bridge-opts': self.setBropts,
                    'up': self.setUp,
                    'down': self.setDown,
                    'pre-up': self.setPreUp,
                    'pre-down': self.setPreDown,
                    'post-down': self.setPostDown,
                    'hostapd': self.setHostapd,
                    'dns-nameservers': self.setDnsNameservers,
                    'dns-search': self.setDnsSearch,
                    'wpa-conf': self.setWpaConf
                }
                for key, value in options.items():
                    if key in roseta:
                        # keep KeyError for validation errors
                        roseta[key](value)
                    else:
                        # Store as if
                        self.setUnknown(key, value)
            except Exception:
                self.reset()
                raise
        else:
            msg = "No arguments given. Provide a name or options dict."
            raise ValueError(msg)

    @staticmethod
    def _ensure_list(dic, key, value):
        """Ensure the data for the given key will be in a list.
        If value is a list, it will be flattened

            Args:
                dic (dict): source dict
                key (string): key to use in dic
                value (any): the data. Will be appended into a
                    list if it's not one
        """
        if key not in dic:
            dic[key] = []
        if not isinstance(dic[key], list):
            tmp = dic[key]
            dic[key] = [tmp]
        if isinstance(value, list):
            dic[key] += value
        else:
            dic[key].append(value)
