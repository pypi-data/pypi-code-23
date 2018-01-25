from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

with open(path.join(here, 'VERSION')) as f:
    version = f.read().strip()


setup(
    version=version,
    name='wsgiauth0',
    description='Auth0 middleware for multiple client configurations',
    long_description=long_description,
    packages=['wsgiauth0'],
    setup_requires=[
        'pytest-runner',
        'safety',
    ],
    install_requires=[
        'python-jose>=2.0.2',
        'PyYAML>=3.12',
    ],
    tests_require=[
        'flake8-import-order',
        'mock',
        'moto',
        'pylama',
        'pytest',
        'pytest-cov',
        'pytest-runner',
        'tox',
    ],
    url='https://gitlab.com/dialogue/wsgiauth0',
    license='MIT',
    entry_points={
        'paste.filter_app_factory': [
            'middleware = wsgiauth0:factory',
        ]
    },
    extras_require={
        'dynamodb': [
            'boto3>=1.4',
        ],
    }
)
