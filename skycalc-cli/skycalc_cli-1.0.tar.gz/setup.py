
from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='skycalc_cli',
      version='1.0',
      description='ESO SkyCalc Command Line Interface',
      long_description=readme(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering :: Astronomy',
      ],
      keywords='sky model observatory telescope astronomy ephemeris sun moon',
      url='http://www.eso.org/observing/etc/bin/gen/form?INS.MODE=swspectr' +
          '+INS.NAME=SKYCALC',
      author='European Southern Observatory',
      author_email='usd-help@eso.org',
      license='MIT',
      packages=['skycalc_cli'],
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
      install_requires=[
          'requests',
          'setuptools'
      ],
      entry_points={
          'console_scripts': ['skycalc_cli=skycalc_cli.skycalc_cli:main'],
      },
      include_package_data=True,
      zip_safe=False)
