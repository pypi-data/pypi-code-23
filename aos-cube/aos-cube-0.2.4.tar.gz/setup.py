import os
from setuptools import setup

LONG_DESC = open('pypi_readme.rst').read()
LICENSE = open('LICENSE').read()

install_requires = ['pyserial', 'esptool']

setup(
    name="aos-cube",
    version="0.2.4",
    description="aos command line tool for repositories version control, publishing and updating code from remotely hosted repositories, and invoking aos own build system and export functions, among other operations",
    long_description=LONG_DESC,
    url='https://code.aliyun.com/aos/aos-cube',
    author='aos',
    author_email='aliosthings@service.aliyun.com',
    license=LICENSE,
    packages=["aos", "udc"],
    package_dir = {'aos':'aos', 'udc':'udc'},
    package_data={'aos':[], 'udc':['controller_certificate.pem', 'board/*/*']},
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'aos=aos.aos:main',
            'udc=udc.udc:main',
            'aos-cube=aos.aos:main',
        ]
    },
)
