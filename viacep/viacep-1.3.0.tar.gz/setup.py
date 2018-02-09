from distutils.core import setup
from setuptools import find_packages

import viacep

version = viacep.__version__

install_requires = [
    'requests>=2.9.1'
]

setup(
    name='viacep',
    version=version,
    author='Leonardo Gregianin',
    author_email='leogregianin@gmail.com',
    scripts=['viacep.py', 'test_viacep.py', 'sample.py', 'README.md'],
    url='https://github.com/leogregianin/viacep-python',
    license='LICENSE',
    description='Consulta CEP pelo webservice do ViaCEP.com.br',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown; charset=UTF-8',
    install_requires=install_requires,
    platforms = 'any',
    packages=find_packages(exclude=['tests']),
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],	
)