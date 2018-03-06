from setuptools import setup, find_packages

setup(
    name='pycarbon',
    packages=find_packages(),
    description='A python module for managing YAML config files across multiple environments and files.',
    version='1.0.2',
    license='MIT',
    author='Mark Belles',
    author_email='markbelles@gmail.com',
    url='https://github.com/evilgeniuslabs/pycarbon',
    download_url='https://github.com/evilgeniuslabs/pycarbon/archive/1.0.2.tar.gz',
    keywords=['config', 'configuration', 'files', 'yaml', 'yml'],
    install_requires=['pyyaml==3.12']
)
