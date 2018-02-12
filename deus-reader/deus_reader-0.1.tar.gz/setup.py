from setuptools import setup

setup(name='deus_reader',
      version='0.1',
      description='Tools for reading spherical profiles computed from the DEUS simulations.',
      author='Paul de Fromont',
      author_email='paul.de-fromont@obspm.fr',
      license='MIT',
      packages=['deus_reader'],
      install_requires=[
        'numpy'
      ],
      python_requires='>=3',
      zip_safe=False)
