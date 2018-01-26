# -*- coding: utf-8 -*-

"""
The :mod:`pipesnake.utils` module implements few utils functions, decorators and more.
"""

import re


def to_snake(name):
    """Convert :param name: to snake case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
