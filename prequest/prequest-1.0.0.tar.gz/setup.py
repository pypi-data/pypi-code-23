from setuptools import setup
from codecs import open

# Parse the version from the module without importing
version = '0.0.0'
with open('prequest/__init__.py') as f:
    for line in f:
        if line.find('__version__') >= 0:
            version = line.split('=')[1].strip().strip('"').strip("'")
            break

# Retrieve dependencies
with open('requirements.txt', 'r') as f:
    reqs = f.readlines()
with open('test-requirements.txt', 'r') as f:
    test_reqs = f.readlines()

# Retrieve readme
with open('README.rst', 'r') as f:
    long_desc = f.read()

setup(
    name='prequest',
    version=version,
    description='Light wrapper around the requests library that facilitates data backup to a configurable data source.',
    long_description=long_desc,
    author='Boston University Software & Application Innovation Lab',
    author_email='hicsail@bu.edu',
    url='https://github.com/Data-Mechanics/prequest',
    packages=['prequest'],
    install_requires=reqs,
    tests_require=test_reqs,
    test_suite='nose.collector',
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ),
)
