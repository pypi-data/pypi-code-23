from setuptools import setup

setup(
    name='mtbparser',
    version='0.2.5',
    license='MIT',
    url='https://github.com/qbicsoftware/qbic.mtbparser',
    description='A module that parses different diagnostic variant data.',
    long_description=open('DESCRIPTION.rst').read(),
    author='Sven Fillinger',
    author_email='sven.fillinger@qbic.uni-tuebingen.de',
    packages=['mtbparser'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License"
    ]
)
