"""
Setup file for DSA config
"""

from setuptools import setup

setup(
    name='dsa_config',
    version='1.0',
    description='DSC server configuration, DSC REST APIs',
    packages=["dsa_config"],
    install_requires=[
        'requests',
        'socket',
        'tdtestpy'
    ],
    package_data={'json': ['payload_files/*.json']},
    include_package_data=True,
    zip_safe=False
)