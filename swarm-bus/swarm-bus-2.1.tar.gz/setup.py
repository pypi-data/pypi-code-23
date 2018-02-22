"""
Swarm bus
"""
from setuptools import find_packages
from setuptools import setup

__version__ = '2.1'
__license__ = 'GPL License'

__author__ = 'The Swarm Team'
__email__ = 'dev@hiventy.com'

__url__ = 'https://bitbucket.org/monalgroup/swarm-bus'


install_requires = [
    'amqp==2.2.1',
    'boto==2.45.0',
    'kombu==4.0.2',
    'vine==1.1.4',
]


setup(
    name='swarm-bus',
    version=__version__,
    license=__license__,

    description='AMQP layer for communicating with the ESB.',
    long_description=__doc__,
    keywords='ESB, tools, swarm, bus',

    packages=find_packages(exclude=('tests', 'tests.*')),

    author=__author__,
    author_email=__email__,
    url=__url__,

    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],

    install_requires=install_requires,

    zip_safe=False,
    include_package_data=True,
)
