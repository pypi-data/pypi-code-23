from setuptools import setup, find_packages
from os.path import join, dirname
import shark1c

setup(
    name='shark1c',
    version=shark1c.__version__,
    py_modules=['shark1c'],
    install_requires=[
        'pycli',
        'scapy',

    ],
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    entry_points='''
        [console_scripts]
        shark1c=shark1c.shark1c:run_sniffer
    ''',
)
