from setuptools import setup

with open('DESCRIPTION.rst') as f:
    long_description = f.read()
    
setup(name='dcpy',
      packages=['dcpy'],
      version='0.1.9',
      description='This is an easy yet powerful python library for interactive data visualization and analysis using dcjs and crossfilter.',
      long_description=long_description,
      author='Washim Ahmed',
      author_email='info@washimahmed.com',
      url='https://github.com/washim/dcpy',
      keywords=['visualization','d3','crossfilter','dc'],
      python_requires='>=3',
      classifiers=['Development Status :: 3 - Alpha','Intended Audience :: Developers','License :: OSI Approved :: MIT License','Programming Language :: Python :: 3.6']
)