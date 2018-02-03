from distutils.core import setup
setup(
  name = 'onc',
  packages = ['onc','onc.V2','onc.V3'], # this must be the same as the name above
  version = '1.22',
  description = 'Ocean 2.0 API Python Client Library.',
  author = 'Ryan Ross and Allan Rempel',
  author_email = 'agrempel@uvic.ca',
  url = 'https://wiki.oceannetworks.ca/display/O2A/Python+Client+Library', # use the URL to the github repo
  download_url = 'https://wiki.oceannetworks.ca/download/attachments/49447606/onc-1.0.tar?api=v2', # I'll explain this in a second
  keywords = ['Oceanography', 'Observatory', 'Sensors'], # arbitrary keywords
  license = 'Apache 2.0',
  classifiers = [],
  install_requires=['requests','python-dateutil','numpy']
)
