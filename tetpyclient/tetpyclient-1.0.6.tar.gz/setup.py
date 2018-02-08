from setuptools import setup

setup(
    name='tetpyclient',
    packages=['tetpyclient'],  # this must be the same as the name above
    version='1.0.6',

    install_requires=['six', 'requests', 'requests_toolbelt'],

    description='Python API Client for Tetration Analytics',
    author='Cisco Tetration Analytics',
    author_email='openapi-dev@tetrationanalytics.com',
    license='Cisco API License'
)
