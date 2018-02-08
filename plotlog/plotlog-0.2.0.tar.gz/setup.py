from setuptools import setup, find_packages


requires = ["pandas>=0.21.1", "matplotlib>=2.1.1", "PyYAML>=3.12"]

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''

setup(
    name='plotlog',
    version='0.2.0',
    description='Plot graph for many log file that is managed by DATE',
    long_description=readme,
    url='https://github.com/s-naoya/plotlog',
    author='SAITO Naoya',
    author_email='saito3110.naoya@gmail.com',
    license='MIT',
    keywords='plot graph logfile',
    packages=find_packages(),
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      plotlog = plotlog.main:main
    """
)
