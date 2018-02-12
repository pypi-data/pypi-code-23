import sys
import re, ast
import os
from os.path import dirname, abspath, join
from setuptools import setup


# Automatically bump version on every build:
with open('src/argus_cli/__init__.py', 'r+') as file:
    contents = file.read()
    _version_scan = re.compile(r'__version__\s+=\s+(.*)')
    version=str(ast.literal_eval(_version_scan.search(contents).group(1)))
    
    new_version = version.split(".")

    if "sdist" in sys.argv or "bdist_wheel" in sys.argv:
        if int(new_version[-1]) > 30:
            new_version[-1] = 0
            new_version[-2] = int(new_version[-2]) + 1
        else:
            new_version[-1] = int(new_version[-1]) + 1

        new_version = ".".join(map(str, new_version))

        print("Bumping version from %s to %s" % (version, new_version))
        file.seek(0)
        file.write(re.sub(version, new_version, contents))
    else:
        new_version = ".".join(map(str, new_version))



with open(join(abspath(dirname(__file__)), "requirements.txt"), 'r') as f:
    install_requirements = f.read()

setup(
    name="argus-toolbelt",
    version=new_version,
    description="A framework for interacting with Argus' APIs",
    author="mnemonic as",
    author_email="opensource@mnemonic.no",
    license="ISC",
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
        "argus_cli": ["src/argus_cli/config.yaml"],
        "argus_api": ["src/argus_api/templates/endpoint.j2"],
        "argus_api": ["src/argus_api/templates/request.j2"],
        "argus_api": ["src/argus_api/templates/init.j2"],
        "argus_api": ["src/argus_api/templates/test_helpers/request.mock.j2"],
    },
    
    setup_requires=install_requirements,
    install_requires=install_requirements,
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
        'License :: OSI Approved :: ISC License (ISCL)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
       'console_scripts': [
           'argus-cli = argus_cli.cli:main',
       ],
    }

)
