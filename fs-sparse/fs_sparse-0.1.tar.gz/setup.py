#!/usr/bin/env python


from setuptools import setup, find_packages

VERSION = "0.1"
DESCRIPTION = "A wrapper for sparse file detection"

setup(
        name="fs_sparse",
        version=VERSION,
        description=DESCRIPTION,
        long_description=open("README.md", "rt").read(),
        author="Feiyi Wang",
        author_email="fwang2@ornl.gov",
        license="Apache",
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: System :: Filesystems',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 2.7',
            ],
        packages=find_packages(),
        platforms=['Linux'],
        python_requires='>=2.7, <3',
        install_requires=['cffi>=1.0.0'],
        setup_requires=['cffi>=1.0.0'],
        cffi_modules=['./sparse/sparse_build.py:ffibuilder']
)
