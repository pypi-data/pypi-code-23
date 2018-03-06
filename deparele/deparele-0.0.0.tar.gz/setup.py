from setuptools import setup

# Package details
setup(
    name="deparele",
    version="0.0.0",
    entry_points={
        "console_scripts": ["deparele = deparele.cli:main"]
    },
    author="Bayu Aldi Yansyah",
    author_email="bayualdiyansyah@gmail.com",
    url="https://github.com/pyk/deparele",
    description="deparele CLI",
    long_description=open("README.rst", "r").read(),
    license="BSD 3-Clause License",
    packages=[
        "deparele"
    ],
    install_requires=[
        "click==6.7",
        "colorama==0.3.9",
    ],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6"
    ]
)
