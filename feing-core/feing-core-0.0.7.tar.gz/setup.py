#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'requests',
    'selenium==2.42.1',
    'tqdm==4.19.4'
]

setup(
    name='feing-core',
    version='0.0.7',

    author='Long Fei',
    author_email='2696250@qq.com',
    url='http://www.feingto.com/',
    license='MIT',

    description='a toolset for python',
    long_description=readme,
    keywords='python tool core',

    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,

    classifiers=[
        'Development Status :: 4 - Beta',
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
