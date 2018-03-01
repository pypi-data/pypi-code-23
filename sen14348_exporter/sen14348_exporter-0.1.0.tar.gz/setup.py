#!/usr/bin/env python

from setuptools import find_packages, setup

ABOUT = {}
with open("sen14348_exporter/__about__.py") as fp:
    exec(fp.read(), ABOUT)


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    author=ABOUT["__author__"],
    author_email=ABOUT["__email__"],
    description=ABOUT["__summary__"],
    long_description=readme(),
    license=ABOUT["__license__"],
    keywords=["sparkfun", "raspberry pi", "rpi", "prometheus", "BME280", "CCS811",
              "i2c", "temperature", "humidity", "pressure", "eco2", "tvoc"],
    url=ABOUT["__uri__"],
    packages=find_packages(),
    install_requires=["Adafruit_BME280", "Adafruit_CCS811", "bme280_exporter",
                      "ccs811_exporter", "prometheus_client"],
    entry_points={
        "console_scripts": [
            "sen14348_exporter = sen14348_exporter.__main__:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Monitoring"
    ]
)