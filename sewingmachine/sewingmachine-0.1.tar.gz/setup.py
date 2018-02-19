from setuptools import setup

setup(name='sewingmachine',
      version='0.1',
      description='the Spectral Equivalent Widths(ing) machine',
      url='http://github.com/jmackereth/sewingmachine',
      author='J. Ted Mackereth',
      author_email='tedmackereth@gmail.com',
      license='MIT',
      packages=['sewingmachine'],
      install_requires = ['numpy', 'scipy', 'matplotlib'],
      zip_safe=False)
