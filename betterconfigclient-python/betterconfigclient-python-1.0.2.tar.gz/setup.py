import uuid
from setuptools import setup
from pip.req import parse_requirements

from betterconfigclient.version import BETTERCONFIGCLIENT_VERSION

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='betterconfigclient-python',
    version=BETTERCONFIGCLIENT_VERSION,
    packages=['betterconfigclient'],
    url='https://github.com/BetterConfig/BetterConfigClient-python',
    license='MIT',
    author='BetterConfig',
    author_email='developer@betterconfig.com',
    description='BetterConfig library for Python. https://betterconfig.com',
    long_description='BetterConfig library for Python. https://betterconfig.com',
    install_requires=reqs,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
)
