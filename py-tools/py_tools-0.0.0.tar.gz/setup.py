from setuptools import setup, find_packages

setup(name='py_tools',
      version='0.0.0',
      description='Important tools for Python',
      url='https://github.com/kevinjuan25/kevinjuan25_py_tools',
      author='Kevin Juan',
      author_email='kj89@cornell.edu',
      license='MIT',
      packages=find_packages(),
      install_requires=['pint','numpy','pandas','matplotlib','scipy'],
      include_package_data=True,
      test_suite="tests",
      zip_safe=False)
