"""Python script Exporter class"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import copy
import json

from traitlets import default

from .templateexporter import TemplateExporter


def strip_cells(notebook):
    clone = copy.deepcopy(notebook)
    del clone['cells']
    return json.dumps(clone)


class EncodedPythonExporter(TemplateExporter):
    """
    Exports a Python code file.
    """
    @default('file_extension')
    def _file_extension_default(self):
        return '.py'

    @default('template_file')
    def _template_file_default(self):
        return 'encoded_python.tpl'

    def _init_resources(self, resources=None):
        resources = super(EncodedPythonExporter, self)._init_resources(resources)
        resources['strip_cells'] = strip_cells
        return resources

    output_mimetype = 'text/x-python'
