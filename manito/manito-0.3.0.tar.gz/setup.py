import os
from setuptools import setup

setup(
        name='manito',
        packages=["manito"],
        url='https://github.com/jk43/manito',
        version='0.3.0',
        author='Alex Hyojun Kim',
        author_email='alex@hotdev.com',
        description=' ',
        license='BSD',
        install_requires=[
            'hdv_logging',
            'hdv_handyman'
            ],
      )