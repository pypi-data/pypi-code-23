"""Default config reading functions"""

import json
import yaml

READERS = {
    "yaml": yaml.load,
    "yml":  yaml.load,
    "json": json.load
}
