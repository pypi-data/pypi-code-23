import os
from setuptools import setup


root_dir = os.path.dirname(__file__)
with open(os.path.join(root_dir, 'version.txt'), 'r') as fp:
    version = fp.read().strip()

with open(os.path.join(root_dir, 'README.rst'), 'r') as fp:
    description = fp.read()


setup(name='PieCrust-Hoedown',
      version=version,
      url='http://bolt80.com/piecrust',
      license='Apache2',
      author='Ludovic Chabant',
      author_email='ludovic@chabant.com',
      description=('Hoedown Markdown formatter for PieCrust '
                   'via Misaka'),
      long_description=description,
      py_modules=['piecrust_hoedown'],
      zip_safe=False,
      install_requires=[
          'PieCrust>=2.0.0',
          'misaka>=2.1.0'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3'])

