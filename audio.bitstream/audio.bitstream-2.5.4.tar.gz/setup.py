#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
pass

# Third-Party Libraries
try:
    import setuptools
except ImportError:
    error = "pip is not installed, refer to <{url}> for instructions."
    raise ImportError(error.format(url="http://pip.readthedocs.org"))

metadata = {'name': 'audio.bitstream', 'version': '2.5.4'}
requirements = \
  {'install_requires': 'bitstream=={0}'.format(metadata['version'])}

info = dict(
  metadata     = metadata,
  code         = dict(packages=setuptools.find_packages()),
  data         = {},
  requirements = requirements,
  scripts      = {},
  commands     = {},
  plugins      = {},
  tests        = {},
)


if __name__ == "__main__":
    kwargs = {k:v for dct in info.values() for (k,v) in dct.items()}
    setuptools.setup(**kwargs)

