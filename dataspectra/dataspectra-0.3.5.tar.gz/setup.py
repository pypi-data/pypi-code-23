from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='dataspectra',
      version='0.3.5',
      description='Creates interactive web visualizations',
      long_description=readme(),
      url='https://dataspectra.org',
      author='Ryosuke Kita',
      author_email='ryo@dataspectra.org',
      license='MIT',
      packages=['dataspectra'],
      install_requires=[
          'xlrd',
          'grpcio==1.9.1',
          'google-cloud-datastore', 
          'scipy',
          'Sphinx',
          'sphinx-autobuild',
          'restructuredtext-lint'
      ],
      scripts=['bin/dataspectra'],
      include_package_data=True,
      zip_safe=False)
