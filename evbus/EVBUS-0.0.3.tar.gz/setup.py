from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='EVBUS',
    version='0.0.3',
    install_requires=['scikit-learn>=0.17', 'numpy>=1.8.2', 'scipy'],
    url='https://github.com/liyao001/EVBUS',
    packages=["EVBUS", ],
    license='Apache 2.0',
    author='Li Yao',
    author_email='yaol17@mails.tsinghua.edu.cn',
    description='Estimate Variance Based on U-Statistics (EVBUS)',
    long_description=long_description,
    classifiers=[
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
)
