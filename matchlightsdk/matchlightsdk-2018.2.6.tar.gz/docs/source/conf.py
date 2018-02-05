"""Sphinx configuration for the Matchlight SDK."""
# -*- coding: utf-8 -*-
import os
import sys

import setuptools_scm


sys.path.insert(0, os.path.abspath('../../src'))
needs_sphinx = '1.3'
extensions = [
    # 'rst2pdf.pdfbuilder',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'Matchlight SDK'
copyright = '2016, Terbium Labs'
author = 'Terbium Labs'
version = setuptools_scm.get_version(root='../..', relative_to=__file__)
release = version
pygments_style = 'sphinx'
html_theme = 'alabaster'
html_theme_options = {
    'fixed_sidebar': True,
    'github_user': 'TerbiumLabs',
    'github_repo': 'python-matchlightsdk',
    'github_button': True,
    'logo': 'logo-stacked-tagline.svg',
    'logo_name': True,
    'sidebar_width': '250px',
}
html_favicon = '_static/favicon.ico'
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ],
}
# intersphinx_mapping = {'https://docs.python.org/': None}
# pdf_documents = [(
#     'index',
#     'rst2pdf',
#     'Matchlight SDK Documentation',
#     'Terbium Labs',
# )]
