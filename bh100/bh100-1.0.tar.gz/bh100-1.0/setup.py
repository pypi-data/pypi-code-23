from setuptools import setup

setup(name='bh100',
      version='1.0',
      py_modules='bh100',
      description='Generates a JSON files of the top Crypto in the market and where you can buy them.',
      url='https://github.com/rbn920/bh100',
      author='Robert Nelson',
      author_email='robertb.nelson@gmail.com',
      install_requires=['click',
                        'coinmarketcap',
                        'requests',
                        'beautifulsoup4'],
      python_requires='>=3',
      entry_points='''
        [console_scripts]
        bh100=bh100:main
      ''',
      license='MIT')
