from setuptools import find_packages
from tcell_agent.version import VERSION

try:
    from setuptools import setup  # noqa
except ImportError:
    from distutils.core import setup

setup(name='tcell_agent',
      version=VERSION,
      description='tCell.io Agent',
      url='https://tcell.io',
      author='tCell.io',
      author_email='support@tcell.io',

      license='Free-to-use, proprietary software.',
      install_requires=[
          "requests[security]",
          "future",
          "pyyaml"
      ],
      tests_require=[
          "requests[security]",
          "future",
          "nose",
          "gunicorn",
          "Django",
          "httmock",
          "Flask"
      ],
      test_suite='nose.collector',
      scripts=['tcell_agent/bin/tcell_agent'],
      packages=find_packages() + ['tcell_agent/pythonpath'],
      package_data={
          'tcell_agent.rust': ['libtcellagent-*.so', 'libtcellagent-*.dylib', 'tcellagent-*.dll']})
