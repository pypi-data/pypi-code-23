from setuptools import setup, find_packages

setup(
    name="generic_report_generator_redshift",
    version="0.0.1",
    author="David Ng",
    author_email="david.ng.dev@gmail.com",
    description=("The generic report generator"),
    url="https://github.com/davidNHK/generic-report-generator",
    download_url="https://github.com/davidNHK/generic-report-generator-redshift/archive/0.0.1.zip",
    license="BSD",
    packages=find_packages("./", exclude=["tests"]),
    keywords=['sqlalchemy', 'job queue', 'worker'],
    classifiers=[],
    install_requires=[
        'pylint',
        'pytest',
        'pytest-cov',
        'twine',
        'sqlalchemy',
        'sqlformat'
    ]
)