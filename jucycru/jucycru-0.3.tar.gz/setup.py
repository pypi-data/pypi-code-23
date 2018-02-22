from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='jucycru',
      version='0.3',
      description='JUICE cruise phase package',
      url='https://bitbucket.org/btorn/jucycru',
      author='Benjamin Torn',
      author_email='btorn@cosmos.esa.int',
      license='MIT',
      packages=['jucycru'],
      install_requires=[
                        'spiceypy',
                        'matplotlib',
                        'numpy',
                        ],
      scripts=['bin/distExampleScript.py'],
      test_suite='nose.collector',
      test_require=['nose'],
      zip_safe=False)
