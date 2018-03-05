import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='bankline-direct-parser',
    version='0.3',
    author='Ministry of Justice',
    author_email='dev@digital.justice.gov.uk',
    url='https://github.com/ministryofjustice/bankline-direct-parser',
    packages=['bankline_parser', 'bankline_parser.data_services'],
    include_package_data=True,
    license='MIT',
    description='Parser for Bankline Direct banking information services',
    long_description=README,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[],
    tests_require=['flake8'],
    test_suite='tests',
)
