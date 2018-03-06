from setuptools import setup, find_packages

version = '0.0.2'

setup(name="helga-pika",
      version=version,
      description=('pika plugin for helga'),
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
      keywords='irc bot pika rabbitmq',
      author='alfredo deza',
      author_email='contact@deza.pe',
      url='https://github.com/alfredodeza/helga-pika',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'helga>=1.7.5',
          'pika',
          'twisted',
      ],
      tests_require=[
          'pytest-twisted',
      ],
      entry_points = dict(
          helga_plugins = [
              'helga_pika = helga_pika:plugin.bus',
          ],
      ),
)
