from setuptools import setup


setup(
    name='mtbconverter',
    version='0.1.1',
    license='MIT',
    url='https://github.com/qbicsoftware/qbic.mtbconverter',
    description='A Python command line tool that parses and converts diagnostic variant data for the Molecular Tumor Board at UKT Tübingen.',
    long_description=open('README.rst').read(),
    author='Sven Fillinger',
    author_email='sven.fillinger@qbic.uni-tuebingen.de',
    packages=['mtbconverter'],
    install_requires=['mtbparser>=0.2.1', 'PyXB==1.2.4'],
    entry_points={
        'console_scripts': [
            'mtbconverter = mtbconverter.main:main']
    },
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
