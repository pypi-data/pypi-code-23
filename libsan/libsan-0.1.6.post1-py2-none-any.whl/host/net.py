# Copyright (C) 2016 Red Hat, Inc.
# This file is part of libsan.
#
# libsan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libsan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libsan.  If not, see <http://www.gnu.org/licenses/>.

"""net.py: Module to manipulate network devices."""

import re #regex
from os import listdir, readlink
import os.path
from os.path import isfile, join, lexists
import socket
import fcntl
import struct
from libsan.host.cmdline import run
import libsan.host.linux

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."


sysfs_class_net_path = "/sys/class/net"

def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:("+ module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:("+ module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:("+ module_name + ") ", string)
    string = re.sub("WARN:", "WARN:("+ module_name + ") ", string)
    print string
    if "FATAL:" in string:
        raise RuntimeError(string)
    return

def is_mac(mac):
    """
    Check if given MAC is  on valid format
    """
    if standardize_mac(mac):
        return True
    return False

def get_nics():
    """
    Return all NICs on the server
    """
    if not os.path.isdir(sysfs_class_net_path):
        #No NIC on this server
        return None

    return listdir(sysfs_class_net_path)

def get_mac_of_nic(nic):
    """
    Given a NIC name return its MAC address
    """
    if not nic:
        _print("FAIL: get_mac_of_nic() - requires nic parameter")
        return None

    mac_path = "%s/%s/address" % (sysfs_class_net_path, nic)
    if not isfile(mac_path):
        _print("FAIL: Could not find path (%s) for MAC address of %s" % (mac_path, nic))
        return None

    ret, mac = run("cat %s" % mac_path, return_output=True, verbose=False)
    if ret != 0:
        _print("FAIL: Could not read MAC from %s" % nic)
        print mac
        return None
    return standardize_mac(mac)

def get_nic_of_mac(mac):
    """
    Give an MAC address return the server interface name
    """
    if not mac:
        _print("FAIL: get_nic_of_mac() - requires mac as argument")
        return None

    if not is_mac(mac):
        _print("FAIL: get_nic_of_mac() - %s does not seem to be a valid MAC" % mac)
        return None

    nics = get_nics()
    if not nics:
        return None

    for nic in nics:
        if mac == get_mac_of_nic(nic):
            return nic

    return None

def get_ip_address_of_nic(nic):
    """
    Get IPv4 of specific network
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = None
    try:
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', nic[:15])
        )[20:24])
    except:
        return None

    return ip

def get_nic_of_ip(ip):
    """
    Given an IP address return the NIC name using it
    """
    if not ip:
        return None

    nics = get_nics()
    if not nics:
        return None

    for nic in nics:
        if ip == get_ip_address_of_nic(nic):
            return nic
    return None

def nic_2_driver():
    """Return a dictionary where nic name is the key and driver name is the value.
Will skip sub interfaces, loop device, tun, vboxnet0.
The arguments are:
\tNone
\treturn_output (Dict): Return a dictionary
Returns:
\tdict: Return dict containing all NICs
"""
    nic_dict = {}
    for nic in listdir(sysfs_class_net_path):
        if (nic == "." or nic == ".." or
                nic == "lo" or                        # loop
                re.match("^tun[0-9]+", nic) or        # TUN NIC
                re.match("^vboxnet[0-9]+", nic) or    # virtualbox NIC.
                re.search(r"\.", nic)):               # sub-interface
            continue
        nic_dict[nic] = driver_of_nic(nic)
    #print nic_dict
    return nic_dict
# End of nic_2_driver()

def driver_of_nic(nic):
    """Given an specific NIC name it returns its driver name
Find out the driver of certain NIC via sysfs file:
    /sys/class/net/eth0/device/driver   # it's a link.
The arguments are:
\tnic: NIC name, eg. eth0
Returns:
\tstr: Driver name
"""
    nic = phy_nic_of(nic)
    nic_file = join(sysfs_class_net_path, nic)
    if not lexists(nic_file):
        print "FAIL: No such NIC exists: %s" % nic
        print nic_file
        return None
    driver_file = "/sys/class/net/%s/device/driver" % nic
    if not lexists(driver_file):
        print "FAIL: path %s does not exist" % driver_file
        return None
    #from a symlink get real path
    real_path = os.readlink(driver_file)
    m = re.match(".*drivers/(.*)$", real_path)
    if not m:
        print "FAIL: Could not find driver name for %s" % nic
        return None
    return m.group(1)
# End of driver_of_nic()


def phy_nic_of(nic):
    """Translate sub-interface of NIC 'eth0.802-fcoe' to physical NIC 'eth0'.
The arguments are:
\tnic: NIC name, eg. eth0.802-fcoe
Returns:
\tstr: phy NIC, eg. eth0
    """
    if not nic:
        return None
    phy_nic = re.sub(r"\..+$", "", nic)
    return phy_nic

def get_pci_id_of_nic(nic):
    """
    From an specific network interface return its PCI ID
    """
    regex_pci_id = libsan.host.linux.get_regex_pci_id()
    sys_path = "%s/%s" % (sysfs_class_net_path, nic)
    link_path = readlink(sys_path)
    #_print("DEBUG: get_pci_id_of_nic - %s" % link_path)
    m = re.search("(%s)/net/%s" % (regex_pci_id, nic), link_path)
    if m:
        return m.group(1)

def get_ip_version(addr):
    """Given an address, tries to check if it is IPv6 or not
The arguments are:
\taddr:     Network address
Returns:
\t4:        Default return if it is not IPv6 address
\t6:        If it is IPv6
    """
    try:
        if socket.inet_pton(socket.AF_INET6, addr):
            return 6
    except socket.error:
        return 4
    #If we can't say the address is IPv6 we return 4, there must be a better way to do it
    return 4

def standardize_mac(mac):
    """
    Usage
        standardize_mac(mac)
    Purpose
        Convert all possiable format mac into stand type:
            (?:[0-9A-F]{2}:){5}[0-9A-F]{2} #like: F0:DE:F1:0D:D3:C9
        Return STRING or ARRAY base on context.
    Parameter
        mac           # any format mac, like "0005.73dd.9a19"
    Returns
        mac
            or
        None
    """
    if not mac:
        return None
    regex_standard_mac = "^(?:[0-9A-F]{2}:){5}[0-9A-F]{2}$"

    mac = mac.lower()
    mac = re.sub("^0x", "", mac)
    mac = re.sub("[^0-9A-Fa-f]", "", mac)
    #If mac given has no ':' we will add it
    if re.match("[0-9a-f]{12}", mac):
        mac_regex = re.compile("(.{2})")
        mac = mac_regex.sub(r"\g<1>:", mac)
        mac = re.sub(":$", "", mac)

    if re.match(regex_standard_mac, mac, re.IGNORECASE):
        return mac

    return None

def if_down(nic_or_mac):
    """
    Bring the interface down
    Parameters:
    \t Interface name or it's MAC address
    """
    if not nic_or_mac:
        _print("FAIL: if_down() - requires nic or mac as argument")
        return None
    
    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
    else:
        nic = nic_or_mac
    
    if run("ifdown %s" % nic):
       return True
    else:
       return False

def if_up(nic_or_mac):
    """
    Bring the interface up
    Parameters:
    \t Interface name or it's MAC address
    """
    if not nic_or_mac:
        _print("FAIL: if_up() - requires nic or mac as argument")
        return None
    
    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
    else:
        nic = nic_or_mac
    
    if run("ifup %s" % nic):
       return True
    else:
       return False
