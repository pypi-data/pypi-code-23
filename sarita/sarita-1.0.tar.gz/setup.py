# coding:utf-8
from setuptools import setup, find_packages

setup(
        name='sarita',
        version='1.0',
        description=('create your site easily'),
        long_description=open('README.rst').read(),
        author='Mr.Lution',
        author_email='mrlution@qq.com',
        maintainer='Mr.Lution',
        maintainer_email='mrlution@qq.com',
        install_requires=[],
        license='GPL License',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        keywords='sarita',
        platforms=['Linux'],
        url='https://uestcman.github.io',
        classifiers=[
            'Programming Language :: Python :: 2.7',
            ],

        )
