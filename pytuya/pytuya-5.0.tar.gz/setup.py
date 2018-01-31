from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytuya',
    version='5.0',
    description='Python interface to ESP8266MOD WiFi smart devices from Shenzhen Xenon',
    long_description='Python interface to ESP8266MOD WiFi smart devices from Shenzhen Xenon',
    url='https://github.com/clach04/python-tuya',
    author='clach04',
    author_email='',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Home Automation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    keywords='home automation',
    packages=["pytuya"],
    install_requires=[
          'pyaes',
      ],
)
