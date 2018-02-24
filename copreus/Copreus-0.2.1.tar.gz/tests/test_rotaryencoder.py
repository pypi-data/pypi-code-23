import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from copreus.drivers.rotaryencoder import RotaryEncoder
from tests.tools import resister_to_pubs

filename = 'config_rotaryencoder.yaml'
resister_to_pubs(filename)
RotaryEncoder.standalone(('-c', filename))

