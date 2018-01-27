# -*- coding: utf-8 -*-
"""The NetworkAdapterValidation tries to validate data before writting,
but it is by no means fool proof as it is impossible to have checks
for everything as any package can add its keys.
"""
from __future__ import print_function, with_statement, absolute_import
import socket


VALID_OPTS = {
    'hotplug': {'type': bool},  # Beware, option is really called allow-hotplug
    'auto': {'type': bool},
    'name': {'required': True},
    'address': {'type': 'IP'},
    'netmask': {'type': 'IP'},
    'network': {'type': 'IP'},
    'server': {'type': 'IP'},
    "endpoint": {'type': 'IP'},
    "dstaddr": {'type': 'IP'},
    "local": {'type': 'IP'},
    'broadcast': {'type': 'BROADCAST_IP'},
    'gateway': {'type': 'IP'},
    'dad-attempts': {'type': int},
    'metric': {'type': int},
    'mtu': {'type': int},
    'unit': {'type': int},
    'autoconf': {'type': int},
    'leasehours': {'type': int},
    'accept_ra': {'type': int},
    'leasetime': {'type': int},
    'privext': {'type': int, "in": [0, 1, 2]},
    'preferred-lifetime': {'type': int},
    "loopback": {"in": ["on", "off"]},
    "listenonly": {"in": ["on", "off"]},
    "triple": {"in": ["on", "off"]},
    "oneshot": {"in": ["on", "off"]},
    "berr": {"in": ["on", "off"]},
    'bridge-opts': {'type': dict},
    'dns-nameservers': {'type': 'IPList'},
    'dns-search': {'type': 'URIList'},
    "mode": {"in": ["GRE", "IPIP"]},
    'scope': {'in': ['global', 'link', 'host', 'site', 'host']},
    'addrFam': {'in': ['inet', 'inet6', 'ipx', 'can']},
    'source': {'in': ['dhcp', 'static', 'loopback', 'manual',
                      'bootp', 'ppp', 'wvdial', 'dynamic',
                      'ipv4ll', 'v4tunnel', 'auto', "6to4", "tunnel"]},
    'hostapd': {},
    'up': {'type': list},
    'pre-up': {'type': list},
    'post-up': {'type': list},
    'down': {'type': list},
    'pre-down': {'type': list},
    'post-down': {'type': list}
}
REQUIRED_FAMILY_OPTS = {
    "inet": {
        "loopback": (),
        "static": (
            # Address (dotted quad/netmask) required
            "address",
        ),
        "manual": (),
        "dhcp": (),
        "bootp": (),
        "tunnel": ("address", "mode", "endpoint"),
        "ppp": (),
        "wvdial": (),
        "ipv4ll": ()
    },
    "ipx": {
        "static": (),
        "dynamic": ()
    },
    "inet6": {
        "auto": (),
        "loopback": (),
        "static": (),
        "manual": (),
        "dhcp": (),
        "v4tunnel": ("address", ),
        "6to4": ()
    },
    "can": {
        "static": (
            # bitrate (1..1000000) required
            "bitrate",
        )
    }
}


class NetworkAdapterValidation(object):
    """Class to validate an adapter. It validates some options for:
        - presence
        - type
        - authorized values
    """

    def validate_all(self, if_attributes):
        """ Not thorough validations... and quick coded.

            Args:
                if_attributes (dict): the dict representation of the interface

            Raises:
                ValueError: if there is a validation error
        """

        for option, option_validations in VALID_OPTS.items():
            option_value = None
            if option in if_attributes:
                option_value = if_attributes[option]
            self.validate_one(option, option_validations, option_value)

        # Logic checks from man interfaces
        if "addrFam" in if_attributes:
            family_opts = REQUIRED_FAMILY_OPTS[if_attributes["addrFam"]]
            try:
                source_opts = family_opts[if_attributes["source"]]
            except KeyError:
                raise ValueError("Family {} must have a source in {}.".format(
                    if_attributes["addrFam"], ", ".join(family_opts.keys())
                ))
            for source_opt in source_opts:
                if source_opt not in if_attributes:
                    msg = "Option {} is required for source {} in family {}."
                    raise ValueError(msg.format(
                        source_opt,
                        if_attributes["source"],
                        if_attributes["addrFam"]
                    ))

    def validate_one(self, opt, validations, val):
        """ Not thorough validations... and quick coded.

            Args:
                opt (str): key name of the option
                validations (dict): contains the validations to checks
                val (any): the option value

            Raises:
                ValueError: if there is a validation error
        """
        if validations is None:
            return
        if not val:
            if 'required' in validations and validations['required'] is True:
                raise ValueError("{0} is a required option".format(opt))
            else:
                return

        if 'type' in validations:
            if validations['type'] == 'IP':
                self.validate_ip(val, opt)
            elif validations['type'] == 'IPList':
                if isinstance(val, list):
                    for ip in val:
                        self.validate_ip(ip, opt)
                else:
                    self.validate_ip(val, opt)
            elif validations["type"] == "BROADCAST_IP":
                self.validate_broadcast_ip(val, opt)
            elif validations["type"] == 'URIList':
                if isinstance(val, list):
                    for search in val:
                        assert isinstance(search, str)
            else:
                if not isinstance(val, validations['type']):
                    msg = "{0} should be {1}".format(opt, validations['type'])
                    raise ValueError(msg)
        if 'in' in validations:
            if val not in validations['in']:
                valid_values = ", ".join(validations['in'])
                msg = "{0} should be in {1}".format(opt, valid_values)
                raise ValueError(msg)

    @staticmethod
    def validate_ip(ip, opt):
        """Validate an IP Address. Works for subnet masks too.

            Args:
                ip (str): the IP as a string
                opt (str): the opt name

            Raises:
                ValueError: on invalid IP
        """
        try:
            socket.inet_aton(ip)
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip)
            except socket.error:
                msg = ("{0} should be a valid IP (got : {1})".format(opt, ip))
                raise ValueError(msg)

    @staticmethod
    def validate_broadcast_ip(ip, opt):
        """Validate an IP Address. Works for subnet masks too.

            Args:
                ip (str): the IP as a string
                opt (str): the opt name

            Raises:
                ValueError: on invalid IP
        """
        if ip not in ("+", "-"):
            try:
                NetworkAdapterValidation.validate_ip(ip, opt)
            except ValueError:
                msg = ("{0} should be a valid IP or a '+' or '-'"
                       "(got : {1})".format(opt, ip))
                raise ValueError(msg)
