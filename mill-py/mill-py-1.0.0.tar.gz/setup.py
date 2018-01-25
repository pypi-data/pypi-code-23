"""Mill's setup module."""

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name="mill-py",
    version="1.0.0",
    description="Python client for interacting with Textile's REST API.",
    url="https://gitlab.com/weareset/mill-py",
    download_url="https://gitlab.com/textileio/mill-py/repository/1.0.0/archive.tar.gz",
    author="Textile",
    author_email="carson@textile.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="REST API Textile Data",
    packages=find_packages(exclude=["tests"]),
    package_data={"mill": ["data/*.json"]},
    tests_require=["pytest"],
    install_requires=["requests[security]", "typing"],
    extras_require={
        "test": ["pytest"],
        "dev": ["tox", "pytest"]
    },
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'millpy=mill:weave',
    #     ],
    # },
)
