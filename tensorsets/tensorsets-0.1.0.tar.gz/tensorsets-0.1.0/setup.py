from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import setuptools


setuptools.setup(
    name='tensorsets',
    version='0.1.0',
    description='Standard datasets for TensorFlow.',
    license='Apache 2.0',
    url='http://github.com/danijar/tensorsets',
    install_requires=[
        'tensorflow',
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Science/Research',
    ],
)
