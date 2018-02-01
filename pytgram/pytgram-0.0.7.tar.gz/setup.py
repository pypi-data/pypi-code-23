import os
from setuptools import setup


with open(os.path.join('pytgram', '__init__.py'), 'r') as init_file:
    init_data = {}
    for line in init_file:
        if line.startswith('__'):
            meta, value = line.split('=')
            init_data[meta.strip()] = value.strip().replace("'", '')

setup(
    name='pytgram',
    version=init_data['__version__'],
    packages=['pytgram', 'tests'],
    url='https://github.com/artcom-net/pytgram',
    license=init_data['__license__'],
    author=init_data['__author__'],
    author_email=init_data['__email__'],
    description='Library to create Telegram Bot based on Twisted',
    long_description=open('README.rst').read(),
    install_requires=open('requirements.txt').read().split(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',

    ]
)
