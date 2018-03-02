import os
from setuptools import setup, find_packages
from aztk_cli import constants
from aztk import version

data_files = []


def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


data_files = package_files("config") + package_files("node_scripts")

print("Dir", data_files)
setup(
    name='aztk',
    version=version.__version__,
    description=
    'Utility for data engineers or platform developers to Run distributed jobs in Azure',
    url='https://github.com/Azure/aztk',
    author='Microsoft',
    author_email='jiata@microsoft.com',
    license='MIT',
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "azure-batch==3.0.0",
        "azure-mgmt-batch==5.0.0",
        "azure-mgmt-storage==1.5.0",
        "azure-storage==0.33.0",
        "pyyaml>=3.12",
        "pycryptodome>=3.4",
        "paramiko>=2.4",
    ],
    package_data={'aztk': data_files},
    scripts=[],
    entry_points=dict(console_scripts=[
        "{0} = aztk_cli.entrypoint:main".format(constants.CLI_EXE)
    ]),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={
        'Documentation': 'https://github.com/Azure/aztk/wiki/',
        'Source': 'https://github.com/Azure/aztk/',
        'Tracker': 'https://github.com/Azure/aztk/issues',
    },
    python_requires='>=3.5',
)
