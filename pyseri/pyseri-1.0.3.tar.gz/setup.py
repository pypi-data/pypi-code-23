from setuptools import setup, find_packages

PACKAGE = "pyseri"
NAME = "pyseri"
DESCRIPTION = "a python object to dict serialzer tool"
AUTHOR = "Taylor"
AUTHOR_EMAIL = "tank357@icloud.com"
URL = "https://github.com/TaylorHere/pyseri"
VERSION = "1.0.3"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description="""

    """,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    packages=['pyseri'],
    package_data={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
    ],
    zip_safe=False,
    install_requires=[],
    entry_points={
    }

)
