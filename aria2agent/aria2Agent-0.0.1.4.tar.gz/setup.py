#!/usr/bin/env python
from setuptools import setup,find_packages

setup(
    name='aria2Agent',
    version='0.0.1.4',
    description='aria2 agent',
    author='Exception',
    author_email='webmaster@pocketdigi.com',
    license='MIT',
    platforms="any",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'License :: Free For Home Use',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='aria2 download',
    setup_requires=[],
    install_requires=['paho_mqtt==1.3.1', 'websocket_client==0.46.0'],
    entry_points={
        'console_scripts': [
            'aria2Agent = aria2_agent.main:main'
        ]
    }
)
