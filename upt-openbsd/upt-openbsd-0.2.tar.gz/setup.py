from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def _install_reqs():
    with open('requirements.txt') as f:
        return f.read().split('\n')

setup(
    name='upt-openbsd',
    author='Cyril Roelandt',
    author_email='tipecaml@gmail.com',
    url='https://framagit.org/upt/upt-openbsd',
    version='0.2',
    description='OpenBSD backend for upt',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires = _install_reqs(),
    packages = find_packages(),
    entry_points = {
        'upt.backends': [
            'openbsd=upt_openbsd.upt_openbsd:OpenBSD',
        ]
    },
)
