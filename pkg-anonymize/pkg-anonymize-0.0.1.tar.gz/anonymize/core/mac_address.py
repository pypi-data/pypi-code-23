#!/usr/bin/python

import subprocess

class MacAddress:
    def set(self, interface):
        # Set interface down
        subprocess.run("ip link set dev {} down".format(interface).split())

        # Change mac address
        subprocess.run("/usr/bin/macchanger -r {}".format(interface).split())

        # Set interface up
        subprocess.run("ip link set dev {} up".format(interface).split())

        # Restart network manager
        subprocess.run("systemctl restart NetworkManager".split())

    def detect(self):
        output = subprocess.run(["ip", "addr"], stdout=subprocess.PIPE)
        output = output.stdout.decode('utf-8')

        for line in output.split("\n"):
            if "state UP" in line:
                return line.split(":")[1].strip()
