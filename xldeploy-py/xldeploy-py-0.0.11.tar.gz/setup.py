from setuptools import setup, find_packages

def readme():
      with open('README.rst') as f:
            return f.read()
try:
      import multiprocessing
except ImportError:
      pass
setup(name='xldeploy-py',
      version='0.0.11',
      description='The python sdk for xldeploy',
      long_description=readme(),
      keywords='xldeploy sdk python xebialabs',
      url='https://github.com/xebialabs/xldeploy-py',
      author='Xebialabs',
      author_email='opensource@xebialabs.com',
      license='MIT',
      packages=find_packages(exclude=["xldeploy.tests.*"]),
      install_requires=[
          'requests==2.11.1'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
