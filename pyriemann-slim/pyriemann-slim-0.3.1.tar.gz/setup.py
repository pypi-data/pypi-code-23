from setuptools import setup, find_packages

setup(name='pyriemann-slim',
      version='0.3.1',
      description='Riemannian Geometry for python for embedded systems',
      url='',
      author='Alexandre Barachant',
      author_email='alexandre.barachant@gmail.com',
      license='BSD (3-clause)',
      packages=find_packages(),
      install_requires=['numpy', 'scipy', 'scikit-learn',  'joblib'],
      zip_safe=False)
