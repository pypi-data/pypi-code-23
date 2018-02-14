#!/usr/bin/python

import os
import subprocess
import sys
import string
import random
import glob

from random import *
from anonymize.core.completer import Completer
from anonymize.core.hostname import Hostname
from anonymize.core.mac_address import MacAddress
from anonymize.core.preference import Preference
from anonymize.core.virtual_private_network import VirtualPrivateNetwork

command = {
    'help'     : ['-h', '--help', 'help'],
    'env'      : ['-c', 'env'],
    'execute'  : ['-e', 'exec', 'execute'],
    'init'     : ['-i', 'init'],
    'set'      : ['-s', 'set'],
    'hostname' : ['-H', 'hostname'],
    'vpn'      : ['-V', 'virtual-private-network'],
    'mac'      : ['-M', 'mac-address']
}

def main():
    try:
        run()
        exit(0)
    except KeyboardInterrupt:
        die("")
    except Exception as ex:
        die(str(ex).strip("'"))


def run():
    if os.geteuid() != 0:
        die('You must be root to run anonymize!')

    if len(sys.argv) == 2:
        if sys.argv[1] in command['init']:
            Preference().initializr()
        elif sys.argv[1] in command['execute']:
            anonymize()
        elif sys.argv[1] in command['env']:
            environment()
        elif sys.argv[1] in command['help']:
            usage()

    elif len(sys.argv) in [3,4]:
        hostname        = Hostname()
        private_network = VirtualPrivateNetwork()
        mac_address     = MacAddress()

        if sys.argv[1] in command['set']:
            if len(sys.argv) == 4:
                if sys.argv[2] in command['hostname']:
                    hostname.set(hostname.rand() if sys.argv[3] == 'random' else sys.argv[3])
                elif sys.argv[2] in command['vpn']:
                    private_network.set(sys.argv[3])
                elif sys.argv[2] in command['mac']:
                    mac_address.set(sys.argv[3])
            else:
                if sys.argv[2] in command['mac']:
                    interface = Preference().interface()
                    if interface != None:
                        mac_address.set(interface)
                elif sys.argv[2] in command['vpn']:
                    path = Preference().private_network_path()
                    private_network.set(path)
                elif sys.argv[2] in command['hostname']:
                    text = Preference().hostname()
                    if text != None:
                        hostname.set(text)

def usage():
    output = [
        "usage anonymize <subcommand> [args] [options]\n"
        " -i, init                     Configure user preference.",
        " -c, env                      Display user preference.",
        " -e, exec, execute            Anonymize personal info with user preference.",
        " -h, --help, help             Display the help and exit.",
        " -v, --version                Output version information and exit.",
        " -s, --set, set               Set virtual private network, hostname or mac address",
        "",
        " anonymize set [args]         [options]    Description",
        " ---------------------------  -----------  ----------------------------------------------------------------------------------------",
        " -V, virtual-private-network  {path}       Connect to an ovpn file. You can send a dir path and anonymize will select a random one.",
        "                                           Ex: anonymize set virtual-private-network /etc/virtual_private_network/",
        " -H, hostname                 {hostname}   Change your computer hostname. You can verify you new one with cat /etc/hostname.",
        "                                           Ex: anonymize set hostname new-hostname",
        " -M, mac-address              {interface}  Change your mac address on interface.",
        "                                           Ex: anonymize set mac-address eth0"
    ]

    die("\n".join(output))


def environment():
    if os.path.isfile('/etc/anonymize/setting') == False:
        die("You need to configure anonymize with: anonymize init")

    setting = Preference().setting()
    output = "Anonymize setting:\n"

    if setting['hostname']:
        output += "- change hostname\n"

    if setting['mac_address'] != None:
        output += "- change mac addres on {}\n".format(setting['mac_address'])

    if setting['virtual_private_network'] != None:
        output += "- connect to vpn: {}\n".format(setting['virtual_private_network'])

    output += "\nYou can change your setting with: anonymize init"
    die(output)


def anonymize():
    if os.path.isfile('/etc/anonymize/setting') == False:
        die("You need to configure anonymize with: anonymize init")

    setting         = Preference().setting()
    hostname        = Hostname()
    private_network = VirtualPrivateNetwork()
    mac_address     = MacAddress()

    if setting['hostname']:
        hostname.set(hostname.rand())
    if setting['mac_address'] != None:
        mac_address.set(setting['mac_address'])
    if setting['virtual_private_network'] != None:
        private_network.set(setting['virtual_private_network'])

def die(text):
    print(text)
    sys.exit(0)

if __name__ == "__main__":
    main()
