# Setup script for installing JumpWayMQTT#
# Author:   Adam Milton-Barker <adammiltonbarker@gmail.com>
# Copyright (C) 2016 Adam Milton-Barker <adammiltonbarker@gmail.com>
# For license information, see LICENSE.txt

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='JumpWayMQTT',
    version="0.1.1",
    author='Adam Milton-Barker',
    author_email='adammiltonbarker@gmail.com',
    url='https://github.com/AdamMiltonBarker/JumpWayMQTT',
    license='',
    description='Python MQTT module that allows developers to communicate with the IoT JumpWay MQTT PaaS',
	package_data={'': ['*.pem']},
    packages=['JumpWayMQTT'],
    install_requires=[
        "paho-mqtt >= 1.2",
    ],
    classifiers=[],
)