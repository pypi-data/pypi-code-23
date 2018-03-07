from setuptools import setup, find_packages

import os

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, "README")) as f:
    long_description = f.read()
    

setup(
    name = "chemfp_converters",
    version = "0.9.1",
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
    entry_points = {
        "console_scripts": [
            # Open Babel's FastSearch
            "fs2fps=chemfp_converters.fs2fps:run",
            "fps2fs=chemfp_converters.fps2fs:run",

            # Dave Cosgrove's Flush
            "flush2fps=chemfp_converters.flush2fps:run",
            "fps2flush=chemfp_converters.fps2flush:run",

            # OEChem's OEFastFPDatabase .fpbin format
            "fpbin2fps=chemfp_converters.fpbin2fps:run",
            "fps2fpbin=chemfp_converters.fps2fpbin:run",
            ],
    },
                
    keywords = "chemfp cheminformatics fingerprint converter FPS FPB",

    install_requires = ["chemfp"],
)
