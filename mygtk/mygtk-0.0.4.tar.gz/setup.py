try:
	from setuptools import setup, find_packages
except ImportError:
	from distutils.core import setup


try:
    import os
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''
    


setup(

	name         =   "mygtk",
	version      =   "0.0.4",
	py_modules   =   ["mygtk"],
    author       =   "oxidworks",
    author_email =   "apps@oxidworks.de",
    url          =   "https://oxidworks.de/",
    #download_url = 'https://github.com/oxidworks/ox_ebaysdk_settingseditor/tarball/0.2.5',
    description  =   "my personal gtk widget extensions",
    long_description = README + '\n\n' + CHANGES,

    packages     =   find_packages(),
    include_package_data = True,
    install_requires = [    
                            'wheel'           ],
    test_suite = 'nose.collector',
    tests_require = ['nose']
    )

