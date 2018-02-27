# http://peterdowns.com/posts/first-time-with-pypi.html

from distutils.core import setup

setup(
  name = 'odie',
  packages = ['odie'],
  version = '1.1.5',
  description = 'Object Database Interaction',
  author = 'Viant Inc.',
  author_email = 'ahunt@viantinc.com',
  url = 'https://github.vianttech.com/techops/odie',
  download_url = 'https://github.vianttech.com/techops/odie',
  keywords = ['salt', 'document', 'odie'],
  data_files = [('bin', ['bin/odie'])],
  scripts = ['bin/odie'],
  classifiers = [],
  install_requires = ['requests', 'colorama', 'terminaltables', 'ruamel.yaml']
)
