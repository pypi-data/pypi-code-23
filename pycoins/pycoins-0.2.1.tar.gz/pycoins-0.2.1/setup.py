from distutils.core import setup

setup(name='pycoins',
      version='0.2.1',
      description='A little command line tool for tracking cryptocurrency prices.',
      url='http://github.com/ptbrodie/coins',
      author='Patrick Brodie',
      author_email='ptbrodie@gmail.com',
      install_requires=[
          'requests==2.18.4',
          'termcolor==1.1.0',
          'terminaltables==3.1.0',
          'beautifulsoup4==4.6.0',
          'dateparser==0.6.0'
      ],
      scripts=['./coins'])
