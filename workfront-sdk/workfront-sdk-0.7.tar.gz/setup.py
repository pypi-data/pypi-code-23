from setuptools import setup, find_packages

setup(name='workfront-sdk',
      version='0.7',
      description='Workfront for Python (SDK)',
      url='https://github.com/BridgeMarketing/workfront-sdk',
      author='Bridge',
      author_email='info@bridgecorp.com',
      license='GPL',
      # packages=['workfront', 'workfront.wf', 'workfront.wf.objects'],
      long_description=open('README.rst').read(),
      packages=find_packages(exclude=('tests')),
      install_requires=['requests==2.18.4'],
      tests_require=['mock', 'nose', 'requests-mock'],
      zip_safe=False)
