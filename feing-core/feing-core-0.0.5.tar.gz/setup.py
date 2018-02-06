#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='feing-core',
    version='0.0.5',

    author='Long Fei',
    author_email='2696250@qq.com',
    url='http://www.feingto.com/',
    license='MIT',

    description='a toolset for python',
    keywords='python tool core',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'selenium==2.42.1',
        'tqdm==4.19.4'
    ],
    zip_safe=False,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
