
from setuptools import setup

setup(
    name='grapa',
    version='0.5.0.1',
    description='Grapa - graphing and photovoltaics analysis',
    author='Romain Carron',
    author_email='carron.romain@gmail.com',
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
    ],
    packages=[
        'grapa',
        'grapa.datatypes',
        'grapa.scripts',
        'grapa.gui',
    ],
    license='MIT',
    url='https://github.com/carronr/grapa/',
	long_description='Grapa is a python package providing a graphical interface and the underlying code dedicated to the visualization, analysis and presentation of scientific data, with a focus on photovoltaic research.',
)
