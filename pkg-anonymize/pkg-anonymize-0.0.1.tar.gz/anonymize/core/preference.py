#!/usr/bin/python

import os
import readline
import glob
import json
from anonymize.core.completer import Completer
from anonymize.core.mac_address import MacAddress
from anonymize.core.hostname import Hostname

message = {
    "hostname"    : "Do you want to generate a new hostname? [Y/n] ",
    "mac_address" : "Do you want to spoof your mac address? [Y/n] ",
    "vpn"         : "Do you want to start a VPN connection? [Y/n] ",
    "user_pref"   : "Do you want to use user.js Firefox configuration file designed to make it more secure? [Y/n] ",
    "user_agent"  : "Do you want to change your Firefox user agent? [Y/n] ",
    "ovpn_dir"    : "What directory contain your ovpn files? ",
    "ovpn_select" : "Please choose a ovpn file. You can select multiple files with *: ",
    "host_select" : "Please choose an hostname: ",
    "selector"    : "Please select an option below:\n{}\nPlease enter your choice: ",
    "err_choice"  : "We could'nt found your choice. Please enter a valid choice: ",
    "err_no_dir"  : "We could'nt found your directory. Try again. ",
    "err_no_ovpn" : "We found no ovpn file. Do you want to choose a new directory? [Y/n] "
}

class Preference:
    default = {
        "hostname" : False,
        "mac_address" : None,
        "virtual_private_network" : None,
        "firefox"  : {
            "user_pref"  : False,
            "user_agent" : False
        }
    }

    def initializr(self):
        hostname    = input(message["hostname"])
        mac_address = input(message["mac_address"])
        interface   = self.interface() if is_true(mac_address) else None
        vpn         = input(message["vpn"])
        path        = self.private_network_path() if is_true(vpn) else None
        #user_pref   = input(message["user_pref"])
        #user_agent  = input(message["user_agent"])

        self.default["hostname"] = is_true(hostname)
        self.default["virtual_private_network"] = path
        self.default["mac_address"] = interface
        #self.default["firefox"]["user_pref"] = is_true(user_pref)
        #self.default["firefox"]["user_agent"] = is_true(user_agent)

        print("Saving your preference...")

        with open('/etc/anonymize/setting', 'w') as file:
            json.dump(self.default, file, indent=2)

    def interface(self):
        net  = os.listdir('/sys/class/net/')
        list = ""
        x    = 0

        current = MacAddress().detect()
        if current != None:
            net.append("current (" + current + ")")

        for interface in net:
            x += 1
            list += (str(x) + ") " + interface + "\n")

        list += ("0) cancel\n")

        buf = input(message["selector"].format(list))
        while buf.isdigit() != True or int(buf) < 0 or int(buf) > x:
            buf = input(message["err_choice"])

        result = int(buf)

        if result == 0:
            return None
        elif result == len(net) and current != None:
            return current
        else:
            return net[result - 1]

    def private_network_path(self):
        readline.set_completer_delims('\t')
        readline.parse_and_bind('tab: complete')

        buf = input(message['ovpn_dir'])
        while os.path.isdir(buf) != True and (os.path.isfile(buf) != True or buf.endswith(".ovpn") != True):
            buf = input(message['err_no_dir'])

        if os.path.isdir(buf):
            if len(glob.glob(buf + '/*.ovpn')) == 0:
                if is_true(input(message['err_no_ovpn'])):
                    return self.private_network_path()
                else:
                    return os.path.join(buf, '*')
            else:
                return self.private_network_preference(buf)

        return buf

    def setting(self):
        with open('/etc/anonymize/setting', 'r') as file:
            return json.load(file)

    def hostname(self):
        list = [
            "1) select random hostname \n"
            "2) define by myself \n"
            "0) cancel \n"
        ]

        pref = input(message["selector"].format(list[0]))
        while pref.isdigit() == False or int(pref) < 0 or int(pref) > 2:
            pref = input(message["err_choice"])

        if pref == '0':
            return None

        elif pref == '1':
            return Hostname().rand()

        elif pref == '2':
           return input(message["host_select"])

    def private_network_preference(self, path):
        list = [
            "1) select ovpn file randomly \n"
            "2) select ovpn file by myself \n"
            "0) cancel \n"
        ]

        pref = input(message["selector"].format(list[0]))
        while pref.isdigit() == False or int(pref) < 0 or int(pref) > 2:
            pref = input(message["err_choice"])

        if pref == '0':
            return None

        elif pref == '1':
            return os.path.join(path, '*')

        elif pref == '2':
            completer = Completer()
            completer.data = os.listdir(path)

            readline.set_completer(completer.get)
            readline.set_completer_delims('')
            readline.parse_and_bind("tab: complete")

            while True:
                choice = os.path.join(path, input(message["ovpn_select"]))
                if len(glob.glob(choice)) > 0:
                    return choice


def is_true(answer):
    return answer.lower() not in ('no', 'n')
