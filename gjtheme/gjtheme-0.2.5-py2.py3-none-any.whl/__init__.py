"""Sphinx GJ Theme

Sphinx GJ Theme is an Apache2 licensed Sphinx theme for projects by Grant
Jenks.

"""

import os


def setup(app):
    app.add_html_theme('gjtheme', os.path.abspath(os.path.dirname(__file__)))

__title__ = 'gjtheme'
__version__ = '0.2.5'
__build__ = 0x000205
__author__ = 'Grant Jenks'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2018 Grant Jenks'
