from setuptools import setup,find_packages

version = "1.3.5.1"

setup(
    name = "FAdo",
    version = version,
    packages = ['FAdo'],
    author = "Rogerio Reis & Nelma Moreira",
    author_email = "rvr@dcc.fc.up.pt",
    description = "Formal Languages manipulation module",
    long_description=open("README.rst").read(),
    include_package_data=True,
    zip_safe=False,
    license = "GPL",
    keywords = "formal languages, finite automata theory, tranducers, regular expressions",
    url = "http://fado.fc.up.pt",
    classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Mathematics",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Operating System :: OS Independent",
            "Programming Language :: Python"
        ],
    install_requires=['setuptools']
)
