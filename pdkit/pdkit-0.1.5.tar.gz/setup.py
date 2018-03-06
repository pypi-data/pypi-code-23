from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='pdkit',
      version='0.1.5',
      description='Parkinson`s Disease Kit',
      url='https://github.com/Birkbeck-Computer-Science-Research/pdkit',
      long_description=readme(),
      keywords='parkinson`s disease kit',
      author='Joan S. Pons',
      author_email='joan@dcs.bbk.ac.uk',
      license='MIT',
      packages=['pdkit'],
      install_requires=[
          'numpy', 'pandas', 'scipy',
      ],
      zip_safe=False)
