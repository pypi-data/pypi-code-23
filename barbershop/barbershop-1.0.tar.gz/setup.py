from setuptools import setup

setup(name='barbershop',
      version='1.0',
      description='A Python package that aids the user in making dynamic cuts to data in various parameter spaces, using a simple GUI.',
      url='https://github.com/ojhall94/barbershop',
      author='Oliver James Hall',
      author_email='ojh251@student.bham.ac.uk',
      license='MIT',
      packages=['barbershop'],
      install_requires=[
            'matplotlib',
            'pandas',
            'numpy'
      ],
      zip_safe=False)
