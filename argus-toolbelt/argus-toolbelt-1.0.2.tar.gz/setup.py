import sys
import os
from os.path import dirname
from setuptools import setup
from setuptools.command.install import install


__VERSION__ = "1.0.2"


def _run_settings_setup(directory):
    """Runs the settings setup script"""
    from subprocess import call
    call([sys.executable, os.path.join(dirname(sys.executable), "toolbelt-setup")], cwd=directory)


class PostInstallScript(install):
    """Custom install that also runs the initial setup script"""
    def run(self):
        _install.run(self)
        self.execute(_run_settings_setup, (self.install_scripts,), msg="Running settings setup script\n")


with open("requirements.txt", 'r') as f:
    install_requirements = f.read()

setup(
    name="argus-toolbelt",
    version=__VERSION__,
    description="A framework for interacting with Argus' APIs",
    author="mnemonic as",
    keywords="argus",
    license="",
    include_package_data=True,
    package_dir={
        "argus_cli": "src/argus_cli",
        "argus_api": "src/argus_api",
        "argus_plugins": "src/argus_plugins",
    },
    packages=[
        # All Argus API modules
        "argus_api", 
        "argus_api.helpers", 
        "argus_api.exceptions", 
        "argus_api.parsers", 

        # All Argus CLI modules
        "argus_cli",
        "argus_cli.helpers",

        # Bundled plugins
        "argus_plugins",
        "argus_plugins.cases",
    ],
    package_data={
        "argus_cli": ["resources/logging_settings.yaml"]
    },
    
    setup_requires=install_requirements,
    install_requires=install_requirements,
    cmdclass={
        "install": PostInstallScript,
        "silent_install": install,
        "bdist_wheel": install,
    },
    scripts=[
        "bin/toolbelt-setup"
    ],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
       'console_scripts': [
           'argus-cli = argus_cli.cli:main',
       ],
    }

)
