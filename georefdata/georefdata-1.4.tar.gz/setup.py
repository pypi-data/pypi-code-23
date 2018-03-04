from distutils.core import setup

setup(
  name = 'georefdata',
  packages = ['georefdata'],
  package_dir = {'georefdata': 'georefdata'},
  package_data = {'georefdata': ['__init__.py', 'data/country_codes.txt', 'data/geonames_feature_classes.txt', 'data/geonames_feature_codes.txt', 'data/timezones.txt']},
  version = '1.4',
  description = 'Country Codes and other Miscellaneous Geo-Spatial Reference Data',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/FirstDraftGIS/georefdata',
  download_url = 'https://github.com/FirstDraftGIS/georefdata/tarball/download',
  keywords = ['location','geo','python'],
  classifiers = [],
)
