from setuptools import setup

setup(
    name="MyDataUtil",
    version="0.1.2",
    author="Jake Liang",
    author_email="010422038@163.com",
    description="This package is for using SQL or FTP in python",
    license="MIT",
    url="https://github.com/DinnerGroup/MyDataUtil",
    packages=['MyDataUtil'],
    install_requires=[
            "cx_Oracle","ConfigParser","logging","paramiko","pyhs2"
            ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
)