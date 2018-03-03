import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from copreus.drivers.bme_280 import BME_280
from tests.tools import resister_to_pubs


filename = 'config_bme_280.yaml'
resister_to_pubs(filename)
BME_280.standalone(('-c', filename))

