from __future__ import print_function

import os
from lxml import etree
from bl.dict import Dict
from .xml import XML

NS = Dict(**{
    "bl": "http://blackearth.us/xml",
})

PATH = os.path.dirname(os.path.abspath(__file__))
JARS = os.path.join(PATH, 'jars')
