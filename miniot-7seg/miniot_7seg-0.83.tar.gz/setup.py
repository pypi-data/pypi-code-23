try:
    # Try using ez_setup to install setuptools if not already installed.
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # Ignore import error and assume Python 3 which already has setuptools.
    pass

from setuptools import setup, find_packages

# try to impor RPi module to see the running system is Raspberry Pi or not.
try:
    import RPi
    is_rpi = True
except:
    is_rpi = False


classifiers = ['Development Status :: 4 - Beta',
               'Operating System :: POSIX :: Linux',
               'Operating System :: MacOS :: MacOS X',
               'Operating System :: Microsoft :: Windows',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: System :: Hardware']

# Changing setup() parameter based on running system.
if is_rpi:
    dlink = ['https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.6.5']
    ireq = ['Adafruit-GPIO>=0.6.5']
else:
    dlink = []
    ireq = []


setup(name              = 'miniot_7seg',
      version           = '0.83',
      author            = 'Atsushi Shibata',
      author_email      = 'shibata@m-info.co.jp',
      description       = 'A library to control Adafruit LED backpack displays, and to show LED image in Jupyter Notebook cell.',
      license           = 'MIT',
      classifiers       = classifiers,
      url               = 'https://github.com/shibats/miniot_7seg/',
      dependency_links  = dlink,
      install_requires  = ireq,
      packages          = find_packages(),
      package_data      = {'': ['js/*.js'],},
      zip_safe          = False)
