from os import path
from setuptools import setup


HERE = path.abspath(path.dirname(__file__))

REQUIREMENTS = (
    'path.py >= 7.0',
    'configobj >= 5.0',
    'click >= 5.1',
    'requests >= 2.4',
)

with open(path.join(HERE, "README.rst")) as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="cluspro_api",
    packages=['cluspro_api'],
    description="Library for submitting and downloading job data from ClusPro.",
    long_description=LONG_DESCRIPTION,
    url="https://bitbucket.org/bu-structure/cluspro_api",
    author="Katie Porter",
    author_email="kaporter@bu.edu",
    license="MIT",
    install_requires=REQUIREMENTS,
    include_package_data = True,
    use_scm_version={'write_to': 'cluspro_api/version.py'},
    setup_requires=['setuptools_scm'],

    entry_points={
        'console_scripts': [
            "cluspro_submit = cluspro_api.cmd_submit:cli",
            "cluspro_download = cluspro_api.cmd_download:cli"
        ]
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='cluspro protein'
)
