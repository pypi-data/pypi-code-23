from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

def _reqs(filename):
    with open(filename) as f:
        return f.read().split('\n')

def _install_reqs():
    return _reqs('requirements.txt')

def _test_reqs():
    return _reqs('test-requirements.txt')

setup(
    name='upt-cpan',
    author='Cyril Roelandt',
    author_email='tipecaml@gmail.com',
    url='https://git.framasoft.org/Steap/sf2cf',
    version='0.1',
    description='XXX',
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
        'upt.frontends': [
            'cpan=upt_cpan.upt_cpan:CPANFrontend',
        ]
    },
)
