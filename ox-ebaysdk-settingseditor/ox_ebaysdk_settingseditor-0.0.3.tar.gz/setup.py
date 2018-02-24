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

	name         =   "ox_ebaysdk_settingseditor",
    packages     =   ['ox_ebaysdk_settingseditor'],
	version      =   "0.0.3",
	py_modules   =   ["ox_ebaysdk_settingseditor"],
    author       =   "oxidworks",
    author_email =   "apps@oxidworks.de",
    url          =   "https://oxidworks.de/",
    description  =   "gtk editor for ebaysdk configfile (experimental)",
    long_description = README + '\n\n' + CHANGES,

    include_package_data = True,
    install_requires = [    'ruamel.yaml',
                            'ebaysdk',
                            'wheel'           ],
    entry_points = {  'console_scripts': [
                            'ox_ebaysdk_settingseditor=ox_ebaysdk_settingseditor:main']},
    test_suite = 'nose.collector',
    tests_require = ['nose']
    )

