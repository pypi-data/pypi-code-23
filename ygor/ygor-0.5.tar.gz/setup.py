from setuptools import setup

setup(
    name='ygor',
    version='0.5',
    packages=['ygor'],
    entry_points = {
      'console_scripts': ['ygor = ygor.__main__:main']
    },
    url='',
    license='',
    author='Hannes Ovrén',
    author_email='hannes.ovren@liu.se',
    description='Minimal experiment runner'
)
