from setuptools import setup

import os

config = {}
currentDir = os.path.abspath(os.path.dirname(__file__))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


with open(os.path.join(currentDir, 'setup_info.py')) as f:
    exec (f.read(), config)


setup(name=config['name'],
      version=config['version'],
      description='Python CLI for XL Deploy',
      long_description=read('README.rst'),
      url='https://docs.xebialabs.com/xl-deploy/concept/xl-deploy-lightweight-cli.html',
      author='XebiaLabs',
      author_email='info@xebialabs.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License'
      ],
      keywords='xldeploy cli python xebialabs',
      package_dir={'': 'src'},
      packages=['xld'],
      entry_points={
          'console_scripts': [
              'xld=xld:main'
          ]
      },
      install_requires=['xldeploy-py', 'fire'],
      include_package_data=True)
