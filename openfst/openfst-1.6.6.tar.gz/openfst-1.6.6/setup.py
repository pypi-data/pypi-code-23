from setuptools import Extension
from setuptools import setup

pywrapfst = Extension(name="pywrapfst",
    extra_compile_args=["-std=c++11", "-Wno-unneeded-internal-declaration",
    "-Wno-unused-function"],
    libraries=["fstfarscript", "fstfar", "fstscript", "fst", "m", "dl"],
    sources=["pywrapfst.cc"])

setup(name="openfst",
    version="1.6.6",
    description="Python wrapper for OpenFst",
    author="Kyle Gorman",
    author_email="kbg@google.com",
    url="http://python.openfst.org/",
    keywords=["natural language processing", "speech recognition",
              "machine learning"],
    classifiers=["Programming Language :: Python :: 2.7",
                 "Development Status :: 5 - Production/Stable",
                 "Environment :: Other Environment",
                 "Environment :: Console",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Topic :: Text Processing :: Linguistic",
                 "Topic :: Text Processing :: Filters",
                 "Topic :: Text Processing :: General",
                 "Topic :: Text Processing :: Indexing",
                 "Topic :: Scientific/Engineering :: Mathematics",
                 "Topic :: Scientific/Engineering :: Artificial Intelligence"],
    ext_modules=[pywrapfst])
