from setuptools import setup, find_packages


def parse_requirements(requirement_file):
    with open(requirement_file) as f:
        return f.readlines()


with open('./README.rst') as f:
    long_description = f.read()


setup(
    name="sbcloud",
    version='0.4.5',
    author="Swimlane LLC",
    author_email="info@swimlane.com",
    packages=find_packages(exclude=('tests', 'tests.*')),
    description="SBCloud",
    long_description=long_description,
    license='UNLICENSED',
    install_requires=parse_requirements('./requirements.txt'),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'sbcloud = sbcloud.cli:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
