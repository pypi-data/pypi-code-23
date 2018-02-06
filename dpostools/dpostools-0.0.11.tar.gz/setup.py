from setuptools import setup

setup(
    name='dpostools',
    version='0.0.11',
    packages=['dpostools', 'dpostools.tests', 'dpostools.yamls'],
    url='https://github.com/BlockHub/blockhubdpostools.git',
    license='MIT',
    author='Charles',
    author_email='karel@blockhub.nl',
    description='generic toolkit for interacting with DPOS chains',
    include_package_data=True
)
