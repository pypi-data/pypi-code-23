from distutils.core import setup
setup(
  name = 'bibdata',
  packages = ['bibdata'],
  version = '0.0.1',
  description = 'Utility code, and sample data, for data science experiments with danish bibliographic data',
  author = 'RasmusErik Voel Jensen',
  author_email = 'pypi@solsort.com',
  url = 'https://github.com/rasmuserik/bibdata',
  package_data={'bibdata': ['content-first.json.gz', 'genre-space.npy', 'meta.json.gz']},
  download_url = 'https://github.com/rasmuserik/bibdata/archive/v0.0.1.tar.gz',
  keywords = ['bibliographic', 'example'],
  python_requires='>=3',
  classifiers = [],
)
