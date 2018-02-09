import os.path as path
from setuptools import setup


def get_readme(filename):
    if not path.exists(filename):
        return ""

    with open(path.join(path.dirname(__file__), filename)) as readme:
        content = readme.read()
    return content


setup(name="mdx_truly_sane_lists",
      version="1.0",
      author='radude',
      author_email='admin@rentry.co',
      description="Extension for Python-Markdown that makes lists truly sane. Custom indents for nested lists and fix for messy linebreaks.",
      license="MIT",
      keywords=["markdown extension", 'markup', 'lists'],
      url="https://github.com/radude/mdx_truly_sane_lists",
      download_url='https://github.com/radude/mdx_truly_sane_lists/archive/1.0.tar.gz',
      packages=["mdx_truly_sane_lists"],
      # long_description=get_readme("README.md"),
      long_description='''
Mdx Truly Sane Lists
====================

|Build Status|

An extension for `Python-Markdown`_ that makes lists truly sane.
Features custom indents for nested lists and fix for messy linebreaks
and paragraphs between lists.

Features
--------

-  ``nested_indent`` option: Custom indent for nested lists. Defaults to
   ``2``. Doesn’t mess with code indents, which is still 4.

-  ``truly_sane`` option: Makes linebreaks and paragraphs in lists
   behave as usually expected by user. No longer adds weird ``p``, no
   extra linebreaks, no longer fuses lists together when they shouldn’t
   be fused (see screenshots and examples below). Defaults to ``True``.

-  Inherits `sane lists`_ behavior, which doesn’t allow the mixing of
   ordered and unordered lists.

Installation
------------

`Pypi`_:
''''''''

.. code:: console

    pip3 install mdx_truly_sane_lists

Directly from git:
''''''''''''''''''

.. code:: console

    pip3 install git+git://github.com/radude/mdx_truly_sane_lists

Usage
-----

Basic:

.. code:: python

    from markdown import markdown

    # Default config is truly_sane: True, nested_indent: 2
    markdown(text='some text', extensions=['mdx_truly_sane_lists']) 

With explicit config:

.. code:: python

    from markdown import markdown

    markdown(text='some text',
             extensions=[
                 'mdx_truly_sane_lists',
             ],
             extension_configs={
                 'mdx_truly_sane_lists': {
                     'nested_indent': 2,
                     'truly_sane': True,
                 }},
             )

Screenshots and examples
------------------------

You can preview the new behaviour live at `rentry.co`_ (uses
``nested_indent: 2, truly_sane: True``)

Some ugly screenshots because I’m lazy and cannot into gimp:

|image1| |image2|

.. _Python-Markdown: https://github.com/Python-Markdown/markdown
.. _sane lists: https://python-markdown.github.io/extensions/sane_lists/
.. _Pypi: https://pypi.python.org/pypi/mdx-truly-sane-lists
.. _rentry.co: https://rentry.co/

.. |Build Status| image:: https://travis-ci.org/radude/mdx_truly_sane_lists.svg?branch=master
   :target: https://travis-ci.org/radude/mdx_truly_sane_lists
.. |image1| image:: https://i.imgur.com/7l2bWLY.png
.. |image2| image:: https://i.imgur.com/Ruwfb2A.png      
''',
      classifiers=[
          "Topic :: Text Processing :: Markup",
          "Topic :: Utilities",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "License :: OSI Approved :: MIT License",
      ],
      install_requires=["Markdown>=2.6"],
      test_suite="mdx_truly_sane_lists.tests")
