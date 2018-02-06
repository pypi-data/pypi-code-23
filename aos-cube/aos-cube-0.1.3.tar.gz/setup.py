import os
from setuptools import setup

LONG_DESC = open('pypi_readme.rst').read()
LICENSE = open('LICENSE').read()

install_requires = [
    'pyserial'
]

setup(
    name="aos-cube",
    version="0.1.3",
    description="aos command line tool for repositories version control, publishing and updating code from remotely hosted repositories, and invoking aos own build system and export functions, among other operations",
    long_description=LONG_DESC,
    url='https://code.aliyun.com/aos/aos-cube',
    author='aos',
    author_email='aliosthings@service.aliyun.com',
    license=LICENSE,
    packages=["aos"],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'aos=aos.aos:main',
            'aos-cube=aos.aos:main',
        ]
    },
)
