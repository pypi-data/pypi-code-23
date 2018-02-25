"""
Chameleon-Client
--------------
Simple client for the chameleon mock server.
"""
from setuptools import setup


setup(
    name='ChameleonClient',
    version='0.1.0',
    url='https://github.com/jolleon/chameleon',
    license='WTFPL',
    author='Jules Olleon',
    author_email='jolleon@gmail.com',
    description=('Simple client for the Chameleon mock server'),
    long_description=__doc__,
    packages=['chameleon'],
    install_requires=[
        'requests>=2.10.0',
        'docker',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)