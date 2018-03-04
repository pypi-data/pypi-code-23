from distutils.core import setup


setup(name='komica_save_file',
      version='1.0.4',
      description='save files from komica',
      keywords=('komica'),
      author='gred0216',
      author_email='betacrunch12345@gmail.com',
      packages=['komica_save_file'],
      install_requires=['requests>=2.13.0', 'beautifulsoup4>=4.6.0'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Programming Language :: Python :: 3.6'],
      python_requires='>=3',
      url='https://github.com/gred0216/komica_save_file',
      download_url='https://github.com/gred0216/komica_save_file/archive/1.0.4.tar.gz',
      )
