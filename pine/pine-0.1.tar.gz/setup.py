import os

from setuptools import setup

NAME = "Brian Curtin"
EMAIL = "brian@python.org"

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Libraries :: Python Modules",
]


if __name__ == "__main__":
    setup(
        name="pine",
        description="A benchmark utility to make requests to a REST API.",
        license="Apache 2",
        url="https://google.com",
        version="0.1",
        author=NAME,
        author_email=EMAIL,
        maintainer=NAME,
        maintainer_email=EMAIL,
        keywords=["benchmarks", "testing"],
        long_description=open(
            os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         "README.rst")).read(),
        scripts=["source/pine.py"],
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=[
            "aiohttp>=3.0",
            "certifi>=2018.1.18",
            ],
    )
