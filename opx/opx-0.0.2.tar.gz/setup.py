from io import open

from setuptools import find_packages, setup

with open('opx/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = [
    'beautifultable',
    'click',
    'click_completion',
    'click_log',
    'colorama',
    'delegator.py',
    'docker',
    'dockerpty',
    'halo',
]

setup(
    name='opx',
    version=version,
    description='',
    long_description=readme,
    author='Tyler Heucke',
    author_email='tyler.heucke@dell.com',
    maintainer='Tyler Heucke',
    maintainer_email='tyler.heucke@dell.com',
    url='https://github.com/theucke/opx-develop',
    license='MIT',

    keywords=[
        'openswitch',
        'opx',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'opx = opx.cli:opx',
        ],
    },
)
