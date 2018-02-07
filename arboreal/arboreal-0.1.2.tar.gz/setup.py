from setuptools import setup

setup(name='arboreal',
      version='0.1.2',
      description='Python package to modularly create decision trees',
      url='http://github.com/ankur-gupta/arboreal',
      author='Ankur Gupta',
      author_email='ankur@perfectlyrandom.org',
      keywords='decision tree modular missing value categorical feature',
      license='MIT',
      packages=['arboreal', 'arboreal.impurity',
                'arboreal.split', 'arboreal.tree'],
      install_requires=['future', 'pandas', 'numpy', 'six'],
      zip_safe=False)
