from setuptools import setup
# from distutils.core import setup

setup(name='garlic',
      packages=['garlic'],
      version='0.0.1',
      description='A parameterized Reinforcement Learning agent',
      author='Theodore Tsitsimis',
      author_email='th.tsitsimis@gmail.com',
      url='https://github.com/tsitsimis/garlic',
      download_url='https://github.com/tsitsimis/garlic/archive/0.0.1.tar.gz',
      keywords=['rl', 'ml'],
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
