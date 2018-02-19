from setuptools import setup

setup(name='aconfig',
      version='1.0.0',
      description='Config Files Manager for JSON and YAML files',
      url='http://github.com/aldarien/aconfig',
      author='Aldarien',
      author_email='aldarien85@gmail.com',
      license='MIT',
      packages=['aconfig'],
      zip_safe=False,
      python_requires='~=3.0',
      install_requires=[
          "pyyaml>=3.0, <4.0"
          ])