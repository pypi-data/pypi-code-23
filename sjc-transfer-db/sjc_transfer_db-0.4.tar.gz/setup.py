from setuptools import setup, find_packages

setup(
    name="sjc_transfer_db",
    version='0.4',
    description='San Jacinto College Transfer Database',
    long_description='',
    classifiers=[
        'Programming Language :: Python :: 3.6'
    ],
    url="http://github.com/mattl3w1s/sjc_transfer_db",
    author="Matt Lewis",
    author_email="matthew.lewis@sjcd.edu",
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',
    ],
    package_data={
        '':'transfer_experiment.db'
    },
    include_package_data=True,
    zip_safe=False
)