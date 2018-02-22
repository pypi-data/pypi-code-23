import subprocess

from setuptools import setup

from hnpy import __version__


def md_to_rst(filename):
    try:
        out = subprocess.check_output('pandoc -t rst -i {}'.format(filename), shell=True)
    except subprocess.CalledProcessError:
        # pandoc is probably not installed
        return 'README: https://github.com/jarhill0/hnpy#hnpy'
    return out.decode('utf-8')  # bytes to str


setup(name='hnpy',
      author='jarhill0',
      author_email='jarhill0@gmail.com',
      description='Yet another object-based Hacker News API wrapper for Python.',
      install_requires=['requests >= 2.18.4'],
      keywords='hacker news api wrapper python3',
      license='MIT',
      long_description=md_to_rst('README.md'),
      packages=['hnpy'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest',
                     'betamax >= 0.8.0',
                     'betamax_serializers >= 0.2.0'],
      test_suite='tests',
      url='https://github.com/jarhill0/hnpy',
      version=__version__)
