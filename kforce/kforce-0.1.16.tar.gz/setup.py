import os
import sys
from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

VERSION = "0.1.16"

sys.path.insert(0, os.path.abspath('lib'))

if __name__ == "__main__":
    setup(
        name="kforce",
        version=VERSION,
        author="Yang Kelvin Liu",
        author_email="ycliuhw@gmail.com",
        license="Apache License 2.0",
        url="https://github.com/ycliuhw/kforce",
        description="KOPS template automation",
        packages=find_packages("lib"),
        scripts=["bin/kforce"],
        keywords=["k8s", "kops", "kubernetes", "template"],
        install_requires=[str(ir.req) for ir in parse_requirements("requirements/base.txt", session=PipSession())],
        zip_safe=False,
        include_package_data=True,
    )
