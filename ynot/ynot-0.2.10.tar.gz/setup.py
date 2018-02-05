import setuptools
import io

from ynot import __version__

distribution = 'ynot'
version = __version__

setuptools.setup(
  name = distribution,
  packages = [distribution],
  #data_files = [('schema', ['schema/transformatorschema.yaml'])],
  install_requires = ['PyYaml', 'jsonpath-ng', 'jsonschema'],
  version = '%s' % version,
  description = 'Yaml-based No-xml Transformation',
  long_description=io.open('README.rst', encoding='utf-8').read(),
  author = 'Jakob Stemberger',
  author_email = 'yaccob@gmx.net',
  license = 'Apache 2.0',
  url = 'https://github.com/%s/ynot' % (distribution),
  download_url = 'https://github.com/yaccob/%s/archive/%s.tar.gz' % (distribution, version),
  keywords = ['yaml', 'json', 'transform', 'xslt', 'jsonpath', 'json-path', 'dump', 'convert', 'validate', 'schema'],
  classifiers = ['Programming Language :: Python :: 2.7'],
  scripts = ['scripts/%s' % (distribution)],
)
