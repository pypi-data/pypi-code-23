#-----------------------------------------------------------------------------
# Name:        setup
# Purpose:    
# Author:      Aric Sanders
# Created:     12/30/2017
# License:     MIT License
#-----------------------------------------------------------------------------
""" Module for distribution """
#-----------------------------------------------------------------------------
# Standard Imports
from setuptools import setup, find_packages

#-----------------------------------------------------------------------------
# Third Party Imports

#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions

#-----------------------------------------------------------------------------
# Module Classes

#-----------------------------------------------------------------------------
# Module Scripts

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':


    setup(
        name='pyMez',
		
		package_dir={'':'src'} ,
        packages=find_packages('src'),  # this must be the same as the name above
		#include_package_data=True,
		package_data = {'': ['*.txt', '*.xml', '*.html', '*.ipynb','*.xsl'],},
        version='0.2.20',
        description='Measurement, Analysis and Data Management Software. To load the API interface use from pyMez import *.',
        author='Aric Sanders',
        author_email='aric.sanders@gmail.com',
        url='https://github.com/aricsanders/pyMez',  # use the URL to the github repo
        download_url='https://github.com/aricsanders/pyMez.git',  # I'll explain this in a second
        keywords=['measurement', 'data handling', 'example'],  # arbitrary keywords
        classifiers=['Programming Language :: Python :: 2.7'],
		license="MIT",
		install_requires=['markdown','numpy','pandas',"Pillow","pdfkit",
		"pdoc","networkx","pyvisa","scipy","matplotlib","pythonnet","pywin32"],
    )
    