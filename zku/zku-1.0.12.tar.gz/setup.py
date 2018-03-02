#!/usr/bin/env python
import os

from distutils.core import setup
from setuptools.command.install import install

SCRIPT_DIR = os.path.dirname(__file__)
if not SCRIPT_DIR:
        SCRIPT_DIR = os.getcwd()

# put together list of requirements to install
install_requires = ['cmdline>=0.1.8', 'sh>=1.11']
REQUIREMENTS = os.path.join(SCRIPT_DIR, 'requirements.txt')
if os.path.exists(REQUIREMENTS):
    with open(REQUIREMENTS) as fh:
        for line in fh.readlines():
            if line.startswith('-'):
                continue

            install_requires.append(line.strip())

long_description = ''
README = os.path.join(SCRIPT_DIR, 'README.md')
if os.path.exists(README):
    long_description = open(README, 'r').read()


def get_data_files(base):
    for dirpath, _, filenames in os.walk(base):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


# http://stackoverflow.com/a/36902139/703144
class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        os.system("systemctl daemon-reload")
        install.run(self)


data_files = [
    ('config', list(get_data_files('config'))),
    ('/etc/systemd/system', ['etc/systemd/system/zymkey-filesystem@.service']),
    ('share/zymkey/examples', get_data_files('examples')),
    ('share/zymkey/doc', ['latex/zk_app_utils.py.pdf']),
    ('', ['LICENSE.txt'])
]

setup(name='zku',
      version='1.0.12',
      description='Zymkey utilities',
      author='Zymbit, Inc.',
      author_email='code@zymbit.com',
      packages=[
          'zymkey',
          'zymkey.commands',
      ],
      cmdclass={
          'install': PostInstallCommand,
      },
      entry_points={
          'console_scripts': [
              'zymkey = zymkey.entrypoints:main',
          ],
      },
      data_files=data_files,
      long_description=long_description,
      url='https://zymbit.com/',
      license='LICENSE.txt',
      install_requires=install_requires,
)
