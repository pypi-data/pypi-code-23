from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
setup(
    name='make2help',
    version='0.0.1',
    description='Show all target in Makefile',
    url='https://github.com/515hikaru/make2help',
    author='515hikaru',
    author_email='karanodeny@gmail.com',
    classifiers=classifiers,
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'make2help=make2help:main',
        ],
    },
)
