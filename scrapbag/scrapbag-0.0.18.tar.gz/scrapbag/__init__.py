# -*- coding: utf-8 -*-
""" Reusable utils module."""

__all__ = [
    "collections",
    "csvs",
    "dates",
    "files",
    "geo",
    "pdf",
    "spss",
    "strings",
    "version"]

# BAD PRACTICE: the wildcard is bad but usefull.
from .collections import *
from .csvs import *
from .dates import *
from .files import *
from .geo import *
from .pdf import *
from .spss import *
from .strings import *
from .version import *
