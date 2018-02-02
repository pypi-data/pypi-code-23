from distutils.core import setup
setup(
  name = 'pipulate',
  packages = ['pipulate'],
  version = '0.1.7',
  download_url = 'https://github.com/miklevin/pipulate/archive/0.1.7.tar.gz',
  description = 'Simplifes Google Spreadsheet Automation',
  long_description='Simplifies Google OAuth2 login and Ties together GSpread and Pandas with a clea API for manipulating data in Google spreadsheets for SEO SERP tracking, dashboards, and other investigations.',
  author = 'Mike Levin, SEO',
  license='MIT',
  author_email = 'miklevin@gmail.com',
  url = 'https://github.com/miklevin/pipulate',
  python_requires='>=3',
  install_requires=['gspread', 'httplib2', 'google-api-python-client'],
  keywords = ['seo', 'google', 'sheets', 'pandas', 'gspread', 'gdata', 'google sheets', 'google spreadsheets', 'google sheet', 'google spreadsheet', 'spreadsheets', 'spreadsheet', 'database', 'databases', 'datascience', 'data science']
)

classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
	'Topic :: Databasea',
     'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.7'
]
