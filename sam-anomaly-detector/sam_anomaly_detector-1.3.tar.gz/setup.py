from os import path

from setuptools import setup

name = 'sam_anomaly_detector'

here = path.abspath(path.dirname(__file__))
module_path = path.join(here, '{}/__init__.py'.format(name))
version_line = [line for line in open(module_path) if line.startswith('__version__')][0]
version = version_line.split('__version__ = ')[-1][1:][:-2]

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=name,
    packages=[name],
    description='Sam media anomaly detector library',
    long_description=long_description,
    version=version,
    url='https://pypi.python.org/pypi/sam-anomaly-detector',
    author='Hossein Jazayeri',
    author_email='hossein@sam-media.com',
    keywords=['forecast', 'fbprophet', 'anomaly-detection'],
    license='Apache-2.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        'numpy',
        'pandas',
        'pystan',
        'fbprophet',
    ],
    python_requires='>=3',
)
