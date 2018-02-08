import os
from setuptools import setup
import json


def requirements_from_pipfile(pipfile=None):
    if pipfile is None:
        pipfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'Pipfile.lock')
    lock_data = json.load(open(pipfile))
    return [package_name for package_name in
            lock_data.get('default', {}).keys()]


install_requires = requirements_from_pipfile()

setup(
    name="gfb",
    version="0.9b4",
    packages=[
        'gfb',
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            'gfb=gfb.app:main'
    },

    # metadata for upload to PyPI
    author="Norm Barnard",
    author_email="norm@normbarnard.com",
    description="Find branches in a remote github repository",
    license="MIT",
    keywords="git github branch branches find search",
    url="https://github.com/barnardn/gfb",
    python_requires='~=3.5',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],
)
