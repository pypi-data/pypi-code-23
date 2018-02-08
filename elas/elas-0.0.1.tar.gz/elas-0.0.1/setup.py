#!/usr/bin/env python3

import distutils.core
import os.path
import sys

if __name__ == "__main__":
    README = "https://github.com/sbp/elas/blob/master/README.md"
    version = "0.0.1"

    distutils.core.setup(
        name="elas",
        version=version,
        author="Sean B. Palmer",
        url="https://github.com/sbp/elas",
        description="Pythonic Elasticsearch API",
        long_description="Documented in `@sbp/elas/README.md <%s>`_" % README,
        platforms="Linux and macOS",
        classifiers=[
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3"
        ]
    )
