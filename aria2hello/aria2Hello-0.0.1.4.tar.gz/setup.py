#!/usr/bin/env python
from setuptools import setup,find_packages

setup(
    name='aria2Hello',
    version='0.0.1.4',
    description='aria2Hello',
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
    keywords='aria2 wechat download',
    setup_requires=[],
    install_requires=['qrcode==5.3', 'paho_mqtt==1.3.1', 'websocket_client==0.46.0', 'Image>=1.5.17'],
    entry_points={
        'console_scripts': [
            'Aria2Controller = aria2.main:main'
        ]
    }
)
