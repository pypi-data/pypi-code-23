from os import path
from pip.req import parse_requirements
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def _reqs(filename):
    return [str(ir.req) for ir in parse_requirements(filename, session='')]

def _install_reqs():
    return _reqs('requirements.txt')

def _test_reqs():
    return _reqs('test-requirements.txt')

setup(
    name='upt-cpan',
    author='Cyril Roelandt',
    author_email='tipecaml@gmail.com',
    url='https://framagit.org/upt/upt-cpan',
    version='0.2.1',
    description='CPAN frontend for upt',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires = _install_reqs(),
    tests_require = _test_reqs(),
    packages = find_packages(),
    entry_points = {
        'upt.frontends': [
            'cpan=upt_cpan.upt_cpan:CPANFrontend',
        ]
    },
)
