#!/usr/bin/env python
from setuptools import setup

setup(
    name="pivotal2pdf",
    author="Christopher Strack",
    author_email="csk@ableton.com",
    description="A utility to generate PDFs from CSV exported from Pivotal",
    url="https://github.com/csk-ableton/pivotal2pdf",
    version="1.0",
    packages=["pivotal2pdf"],
    install_requires=['fpdf'],
    include_package_data=True,
    python_requires='>=2.7',
    entry_points={
        'console_scripts': [
            'pivotal2pdf = pivotal2pdf:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: End Users/Desktop',
        'Development Status :: 5 - Production/Stable',
    ],
)
