import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from copreus.drivers.input import Input
from tests.tools import resister_to_pubs

filename = 'config_input.yaml'
resister_to_pubs(filename)
Input.standalone(('-c', filename))

