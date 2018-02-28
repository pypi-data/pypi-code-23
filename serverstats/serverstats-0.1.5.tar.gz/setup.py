from setuptools import setup
from setuptools import find_packages

setup(
    name="serverstats",
    version="0.1.5",
    description="Collect important system metrics from a server and log them",
    keywords="serverstats",
    author="Deep Compute, LLC",
    author_email="contact@deepcompute.com",
    url="https://github.com/deep-compute/serverstats",
    license='MIT',
    dependency_links=[
        "https://github.com/deep-compute/serverstats",
    ],
    install_requires=[
        "basescript==0.2.0",
        "psutil==5.4.3",
        "deeputil==0.1.2",
    ],
    package_dir={'serverstats': 'serverstats'},
    packages=find_packages('.'),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
    test_suite = 'test.suite',
    entry_points={
        "console_scripts": [
            "serverstats = serverstats:main",
        ]
    }
)
