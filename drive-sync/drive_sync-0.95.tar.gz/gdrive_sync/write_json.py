from __future__ import absolute_import
import json
from os import sys, path

try:
    # set directory for relativistic import
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import file_add
except ImportError:
    from . import file_add


format_add = {
    "application/vnd.google-apps.document": ".docx",
    "application/vnd.google-apps.form": ".xlsx",
    "application/vnd.google-apps.presentation": ".pptx",
    "application/vnd.google-apps.spreadsheet": ".xlsx"
}


with open(file_add.format_dict, "w+") as f:
    json.dump(format_add, f)
