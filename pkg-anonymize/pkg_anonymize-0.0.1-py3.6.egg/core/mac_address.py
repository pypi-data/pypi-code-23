#!/usr/bin/python

import subprocess

class MacAddress:
    def set(self, interface):
        active = self.is_active()

        if active:
            subprocess.call("ip link set dev {} down".format(interface).split())

        subprocess.call("/usr/bin/macchanger -r {}".format(interface).split())

        if active:
            subprocess.call("ip link set dev {} up".format(interface).split())
            subprocess.call("systemctl restart NetworkManager".split())

    def is_active(self):
        return self.detect != None

    def detect(self):
        output = subprocess.call(["ip", "addr"], stdout=subprocess.PIPE)
        output = output.stdout.decode('utf-8')

        for line in output.split("\n"):
            if "state UP" in line:
                return line.split(":")[1].strip()
