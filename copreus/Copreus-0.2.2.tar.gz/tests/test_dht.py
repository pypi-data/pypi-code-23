import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from copreus.drivers.dht import DHT
from tests.tools import resister_to_pubs


filename = 'config_dht.yaml'
resister_to_pubs(filename)
DHT.standalone(('-c', filename))