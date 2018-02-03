from setuptools import setup
# from distutils.core import setup

setup(name='programo',
      packages=['programo'],
      version='0.1.0',
      description='Probabilistic Graphical Models in Python',
      author='Theodore Tsitsimis',
      author_email='th.tsitsimis@gmail.com',
      url='https://github.com/tsitsimis/programo',
      download_url='https://github.com/tsitsimis/programo/archive/0.0.1.tar.gz',
      keywords=['graphical models', 'machine learning'],
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',

          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',

          'License :: OSI Approved :: MIT License',

          'Programming Language :: Python :: 3.4'
      ],
      install_requires=[
          'numpy',
      ],
      zip_safe=False
      )
