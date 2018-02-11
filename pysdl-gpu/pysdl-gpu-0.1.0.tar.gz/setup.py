from setuptools import setup, find_packages

from codecs import open
from os import path

current_dir = path.abspath(path.dirname(__file__))

with open(path.join(current_dir, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='pysdl-gpu',
    version='0.1.0',
    description='A wrapper around SDL_gpu',
    long_description=readme,
    url='https://bitbucket.org/Jjp137/pysdl-gpu',
    author='Jjp137',
    author_email='jjp7137@yahoo.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(),
    install_requires=['pysdl2>=0.9.0']
)

