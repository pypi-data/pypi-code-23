"""
"""
from __future__ import division, print_function, unicode_literals

from iirrational.testing import iirrational_data
import Pyro4
import json
import sys


if __name__ == "__main__":
    sys.excepthook = Pyro4.util.excepthook

    Pyro4.config.SERIALIZER = 'dill'
    with open('iirrational_pyro_con.json') as F:
        conf = json.load(F)
    uri = conf['v1']
    uri = uri.strip()
    factory = Pyro4.Proxy(uri)
    dat = iirrational_data('simple2')

    obj = factory.pyrosuper_call('rationalize', dat)

    factory.pyrosuper_call('annotate', obj)
    print(obj)

