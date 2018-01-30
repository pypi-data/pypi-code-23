from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'VERSION')) as f:
    version = f.read().strip()

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('requirements-tests.txt') as f:
    test_requirements = f.readlines()

setup(
    author='Hugo Duncan',
    author_email='hugo@hugoduncan.org',
    name='menhir',
    description="A build tool for monolithic repositories",
    version=version,
    packages=find_packages(),
    data_files=[('.', [
        'VERSION',
        'requirements.txt',
        'requirements-tests.txt'
    ])],
    setup_requires=['pytest-runner'],
    install_requires=requirements,
    extras_require={
        ":python_version=='2.7'": ["functools32"]
    },
    tests_require=test_requirements,
    include_package_data=True,
    url='https://github.com/dialoguemd/menhir',
    license='MIT',
    entry_points={
        'console_scripts': [
            'menhir = menhir.script:main',
        ]
    }
)
