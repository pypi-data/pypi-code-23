from setuptools import setup, find_packages

packages = []
install_requires = ['requests>=2.14.2','bs4']
ext_modules = []

setup(
    name='npdoc',
    author="Alex Deich",
    author_email='<alex.d.deich@gmail.com>',
    url="https://github.com/deichdeich/npdoc",
    license="3-clause BSD style license",
    description="In-notebook NumPy man pages",
    long_description=open("README.rst").read(),
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Natural Language :: English",
                 "Programming Language :: Python"],
    platforms='any',
    version='1.0.1',
    packages=packages,
    ext_modules=ext_modules,
    install_requires=install_requires,
)