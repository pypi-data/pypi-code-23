# Copyright 2013-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.

# This module has no docstring because it is to be execfile'd
# from `setup.py`, `etgen/__init__.py` and possibly some external
# tools, too.

install_requires = ['six', 'django', 'future']

SETUP_INFO = dict(
    name='etgen',
    version='0.0.1',
    install_requires=install_requires,
    description="Use ElementTree to generate html, rst and other markup",
    license='Free BSD',
    test_suite='tests',
    author='Luc Saffre',
    author_email='luc@lino-framework.org',
    url="http://etgen.lino-framework.org",
    long_description="""\

Utilities for generating html, xml and rst output from an `ElementTree
<https://docs.python.org/2/library/xml.etree.elementtree.html>`_.

Inspired by Frederik Lundh's `ElementTree Builder
<http://effbot.org/zone/element-builder.htm>`_.

The central project homepage is http://etgen.lino-framework.org

""",
    classifiers="""\
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Framework :: Sphinx :: Extension
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent""".splitlines())

SETUP_INFO.update(packages=[n for n in """
etgen
etgen.intervat
etgen.odf
etgen.sepa
""".splitlines() if n])

SETUP_INFO.update(package_data=dict())


