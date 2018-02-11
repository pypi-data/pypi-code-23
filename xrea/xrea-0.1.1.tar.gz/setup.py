from os import path

from xrea import __version__
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='xrea',
    version=__version__,
    python_requires='>=3.4',
    description='XREA API wrapper',
    long_description=long_description,
    license='BSD-2-Clause',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
    keywords='xrea coreserver',
    author='NAKAMORI Ryosuke',
    author_email='me@tpdn.kim',
    url='https://github.com/tpdn/xrea',
    packages=['xrea'],
    package_dir={'xrea': 'xrea'},
    install_requires=['requests']
)
