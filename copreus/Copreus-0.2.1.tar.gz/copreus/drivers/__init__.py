#from copreus.drivers.adc import ADC
#from copreus.drivers.bme_280 import BME_280
#from copreus.drivers.dac import DAC
#from copreus.drivers.dht import DHT
#from copreus.drivers.epaper import EPaper
#from copreus.drivers.epaper import EPaperConstants
#from copreus.drivers.epaper import EPaperMQTTMessageConverter
#from copreus.drivers.input import Input
#from copreus.drivers.output import Output
#from copreus.drivers.rotaryencoder import RotaryEncoder

import os
import glob
import ast
import _ast


def get_drivers():
    """Get all classes and their modules that are silbilings of baseclasses.adriver.ADriver."""

    def extract_class_info(class_entry, filename, package, child_of=None):
        result = {
            "name": class_entry.name,
            "path": filename,
            "module": package + "." + filename[:-3].split('/')[-1],
            "bases": []
        }
        for b in class_entry.bases:
            result["bases"].append(b.id)

        if child_of is not None:
            if not child_of in result["bases"]:
                result = None

        return result

    path = os.path.abspath(os.path.dirname(__file__))
    files = glob.glob(path + "/*.py")
    class_list = {}
    for filename in files:
        with open(filename, 'r') as myfile:
            sourcecode = myfile.read()
        tree = ast.parse(sourcecode)
        classes = [cls for cls in tree.body if isinstance(cls, _ast.ClassDef)]
        for c in classes:
            ci = extract_class_info(c, filename, 'copreus.drivers', child_of="ADriver")
            if ci:
                class_list[ci["name"].upper()] = ci

    return class_list
