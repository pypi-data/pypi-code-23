"""
Functions for rendering

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.

Parts of this code are reworked from the rendernb checklet for Momotor <momotor.org>.
"""

from nbformat import NotebookNode
from typing import Any, Dict
from argparse import Namespace
from nbconvert import HTMLExporter
from .inline_attachments import InlineAttachmentsPreprocessor
from textwrap import dedent

# ADDITIONAL_STYLES = dedent("""\
#     div.inner_cell, div.output_subarea {
#       flex: 1 auto !important;
#     }
#     """)
#
# HTML_FRAME = dedent("""\
#     <html>
#     <head>
#     <style>
#     {css}
#     </style>
#     <script>
#     {javascript}
#     </script>
#     </head>
#     <body>
#     {body}
#     </body>
#     </html>
#     """)


def render_nb(notebook: NotebookNode, args: Namespace) -> Dict[str, Any]:
    """Render notebook as html.
    Uses ``args.template_file`` as template.

    :param notebook: notebook to render
    :param args: options
    :return: html
    """
    resources = {}

    iapp = InlineAttachmentsPreprocessor()
    notebook, resources = iapp.preprocess(notebook, resources)

    html_exporter = HTMLExporter()
    # TODO also set/extend html_exporter.template_path from option?
    html_exporter.template_file = args.template_file

    html, resources = html_exporter.from_notebook_node(notebook)

    # properties = {
    #     'body': html,
    #     'css': '',
    #     'javascript': ''
    # }

    # return HTML_FRAME.format(**properties)
    return html
