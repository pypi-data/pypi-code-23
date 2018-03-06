#!/usr/bin/env python
from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


if __name__ == '__main__':
    setup(
        name='meconf',
        use_scm_version=True,
        description='''''',
        long_description=readme(),
        keywords=[
            'config',
        ],
        author="Roland von Ohlen",
        author_email="webwork@rvo-host.net",
        license='',
        url='https://github.com/RockingRolli/meconf',
        scripts=[],
        package_dir={'': 'src'},
        packages=find_packages('src'),
        py_modules=[],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        extras_require={
            'develop': [
                'pytest==3.4.1',
                'pytest-cov==2.5.1',
                'pytest-env==0.6.2',
                'pylint==1.8.2',
                'twine==1.9.1',
            ]
        },
        setup_requires=[
            'setuptools_scm'
        ],
        install_requires=[
        ],
        dependency_links=[],
        zip_safe=True
    )
