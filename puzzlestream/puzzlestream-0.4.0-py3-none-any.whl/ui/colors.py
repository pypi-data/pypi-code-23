# -*- coding: utf-8 -*-
"""Colour module.

Usage:
- Update current colours first via update using the given yaml file.
- get colour by name using get
- parse a qss file using parseQSS
"""

import yaml

__colors = {}


def update(path):
    """Update current colours using the given yaml file.

    Args:
        path (str): Path to the yaml file.
    """
    with open(path, "r") as f:
        __colors.update(yaml.load(f))


def get(name):
    """Get colour by name."""
    if name in __colors:
        return __colors[name]
    return "black"


def parseQSS(path):
    """Parse QSS file using current colours.

    Args:
        path (str): Path to the QSS file.
    """
    with open(path, "r") as f:
        qss = f.read()

    for key in __colors:
        if key.startswith("Qt"):
            qss = qss.replace(key, __colors[key])

    return qss
