from setuptools import setup, find_packages

import os

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, "README")) as f:
    long_description = f.read()
    

setup(
    name = "chemfp_converters",
    version = "0.9",
    description = "Convert cheminformatics fingerprint files to/from the chemfp formats",
    long_description = long_description,
    
    author = "Andrew Dalke",
    author_email =  "dalke@dalkescientific.com",
    url = "https://bitbucket.org/dalke/chemfp_converters",
    license = "MIT",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Chemistry",
        ],

    packages = ["chemfp_converters"],
    scripts = [
        # Open Babel's FastSearch
        "fs2fps",
        "fps2fs",

        # Dave Cosgrove's Flush
        "flush2fps",
        "fps2flush",

        # OEChem's OEFastFPDatabase .fpbin format
        "fpbin2fps",
        "fps2fpbin",
        ],
    
    keywords = "chemfp cheminformatics fingerprint converter FPS FPB",

    install_requires = ["chemfp"],
)
