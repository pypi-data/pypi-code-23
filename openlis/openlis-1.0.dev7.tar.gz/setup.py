from setuptools import setup, find_packages

setup(name='openlis',
      version='1.0.dev7',
      description='Implementation of Learned Index Structures',
      url='http://github.com/amorten/openlis',
      author='Andrew Morten',
      author_email='andio.m@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['numpy','tensorflow'],
      python_requires='>=3',
      zip_safe=False)
