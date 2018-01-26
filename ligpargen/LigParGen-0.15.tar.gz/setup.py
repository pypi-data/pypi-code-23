from setuptools import setup, find_packages

setup(
  name = 'LigParGen',
  packages = ['LigParGen'], # this must be the same as the name above
  version = '0.15',
  description = 'Python script to provide BOSS generated OPLS-AA/CM1A(-LBCC) parameters for organic molecules and ligands.',
  author = 'Leela S. Dodda, Matthew C. Robinson',
  author_email = 'leela.dodda@yale.edu,matthew.robinson@yale.edu',
  license='MIT',
  url='https://bitbucket.org/leelasd/lpg_jan22_2018',
  keywords = ['computational chemistry', 'force fields', 'molecular dynamics'],
  classifiers = [
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        ],
  install_requires=['numpy','pandas'],
  entry_points={
        'console_scripts': [
            'LigParGen=LigParGen.Converter:main',
        ],
    },

)
