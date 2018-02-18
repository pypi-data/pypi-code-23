from setuptools import setup
setup(
  name = 'niltechArduino',
  packages = ['niltechArduino'], # this must be the same as the name above
  version = '1.0',
  description = 'A lib to automatically detect and give usb port which is connected to arduino and also extract incoming data using start and stop bytes',
  author = 'Vaibhav VK - Niltech',
  author_email = 'vaibhav@niltech.in',
  #url = 'https://github.com/peterldowns/mypackage', # use the URL to the github repo
  #download_url = 'https://github.com/peterldowns/mypackage/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['Arduino','getPort','readData','extractData'], # arbitrary keywords
  classifiers = [],
)
