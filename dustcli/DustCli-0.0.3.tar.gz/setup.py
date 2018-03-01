
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import sys, os

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        develop.run(self)
        os.system('dust init')

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        install.run(self)
        os.system('dust init')

setup(
    name='DustCli',
    version='0.0.3',
    description="dust cli",
    long_description="SCFEE iOS Android 脚手架",
    classifiers=[],
    keywords='',
    author='shaotianchi',
    author_email='shaotianchi@souche.com',
    url='https://tangeche.com',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    install_requires=[
        ### Required to build documentation
        # "Sphinx >= 1.0",
        ### Required for testing
        # "nose",
        # "coverage",
        ### Required to function
        'cement',
        'pbxproj',
        'colorlog',
        ],
    setup_requires=[],
    entry_points="""
        [console_scripts]
        dust = DustCli.cli.main:main
    """,
    namespace_packages=[],
    )
