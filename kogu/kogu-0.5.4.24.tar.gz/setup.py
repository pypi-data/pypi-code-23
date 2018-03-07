import os
from setuptools import setup, find_packages

def _get_version():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir_name, 'VERSION')) as version_file:
        return version_file.read().strip()

setup(
    name='kogu',
    version=_get_version(),
    description='Kogu helper library',
    url='https://kogu.io',
    author='Proekspert AS',
    author_email='hello@kogu.io',
    license='MIT',
    packages=find_packages(),
    python_requires='>=2.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
)
