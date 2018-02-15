from setuptools import setup, find_packages
setup(
    name="Bulk-Import",
    version="0.1",
    packages=find_packages(),
    scripts=['install.sh','Bulk-Import.sh'],

    install_requires=['boto3', 'botocore', 'httplib2', 'wheel'],

    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],

    author="Miguel Ortiz",
    author_email="miguel.ortiz@compucom.com",
    description="Package that includes dependencies for Bulk-Import",
    keywords="HIRO ARAGO Bulk-Import",
)