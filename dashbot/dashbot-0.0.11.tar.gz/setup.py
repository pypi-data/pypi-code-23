
from setuptools import setup
from codecs import open
from os import path

from dashbot import version

here = path.abspath(path.dirname(__file__))
 
# Get the long description from the README file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()
 
setup(
    name='dashbot',
  
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version.__version__,
  
    description='Dashbot Python SDK',
    long_description=long_description,
  
    # The project's main homepage.
    url='https://github.com/actionably/dashbotpy',
  
    # Author details
    author='Ryan Mortensen',
    author_email='ryanm@dashbot.io',
  
    # Choose your license
    license='MIT',
  
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
  
    # What does your project relate to?
    keywords='dashbot, alexasdk, skill',
  
    packages=['dashbot'],
  
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. 
    install_requires=['requests'],
  
  
)
