#!/usr/bin/python

import os
import glob
import random
import subprocess
from anonymize.core.preference import Preference

class VirtualPrivateNetwork:
    def set(self, path):
        preference = Preference()
        if os.path.isdir(path):
            if len(glob.glob1(path, "*.ovpn")) > 0:
                path = preference.private_network_preference(path)
                return self.connect(
                    self.select(path)
                )
        else:
            list = glob.glob(path)
            if len(list) > 1:
                file = self.select(path)
                if file != None:
                    return self.connect(file)
            elif len(list) == 1 and list[0].endswith(".ovpn"):
                return self.connect(list[0])

        print("We could'nt found any ovpn file in {}".format(path))

    def select(self, path):
        list = glob.glob(path)
        if len(list):
            ovpn = random.choice([x for x in list if x.endswith(".ovpn")])
            return os.path.join(path, ovpn)

    def connect(self, ovpn):
        subprocess.call("/usr/bin/openvpn --config {}".format(ovpn).split())
