from setuptools import setup

setup(name='sharelock_utils',
      version='0.3.13',
      description='Simple utils for Sharelock',
      url='',
      author='Rani',
      author_email='rani@snip.today',
      license='MIT',
      packages=['sharelock_utils'],
      install_requires=[
            "sqlalchemy>=1.2.0", "boto3"
        ],
      classifiers=['Programming Language :: Python :: 3.6'],
      zip_safe=False)