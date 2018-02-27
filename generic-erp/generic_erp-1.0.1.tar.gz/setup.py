from setuptools import setup, find_packages
from codecs import open
from os import path

setup(
    name='generic_erp',
    version='1.0.1',
    description='Generic ERP',
    long_description='Generic ERP',
    url='',
    author='BLUEORANGE GROUP',
    author_email='daniel@blueorange.com.ar',
    license='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='Generic ERP',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
)
