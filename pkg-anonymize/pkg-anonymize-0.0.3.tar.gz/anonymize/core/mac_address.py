#!/usr/bin/python

import subprocess
import random
import sys

class MacAddress:
    def set(self, interface):
        list = self.generate()
        current = self.current(interface)

        self.output(current, list)
        self.change(interface, list["addr"])

    def change(self, interface, text):
        subprocess.call("ip link set dev {} down".format(interface).split())
        subprocess.call("ip link set dev {} address {}".format(interface, text).split())
        subprocess.call("ip link set dev {} up".format(interface).split())

        if self.is_active():
            subprocess.call("systemctl restart NetworkManager".split())

    def is_active(self):
        return self.detect != None

    def output(self, current, list):
        text = [
            "[ Generate a new MAC Address ]",
            "MAC Address type    : " + list["type"],
            "Current MAC Address : " + current,
            "New MAC Address     : " + list["addr"].lower()
        ]

        print("\n".join(text))

    def current(self, interface):
        path = '/sys/class/net/' + interface + '/address'
        return open(path, 'r').read().strip()

    def generate(self):
        line = open('/etc/anonymize/data/mac_address').read().splitlines()
        vendor = random.choice(line).split()
        return {
            "type" : " ".join(vendor[3:]),
            "addr" : ":".join([
                vendor[0],
                vendor[1],
                vendor[2],
                '{0:02X}'.format(random.randint(0x00, 0x7f)),
                '{0:02X}'.format(random.randint(0x00, 0xff)),
                '{0:02X}'.format(random.randint(0x00, 0xff))
            ])
        }

    def detect(self):
        output = subprocess.check_output(["ip", "addr"]).decode(sys.stdout.encoding)

        for line in output.split("\n"):
            if "state UP" in line:
                return line.split(":")[1].strip()
