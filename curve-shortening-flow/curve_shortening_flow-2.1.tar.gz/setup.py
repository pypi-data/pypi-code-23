from setuptools import setup

setup(name='curve_shortening_flow',
      version='2.1',
      description='minimization of curavature in 2d',
      url='https://gitlab.gwdg.de/kevin.luedemann/curve_shortening_flow.git',
      author='Alexander Kurz, Kevin Luedemann',
      author_email='alexander.kurz@stud.uni-goettingen.de, kevin.luedemann@stud.uni-goettingen.de',
      license='BSD-3',
      packages=['curve_shortening_flow', 'curve_shortening_flow.animation'],
      install_requires=[
        'numpy',
        'numpydoc',
        'matplotlib',
        'scipy',
        'sphinx'
      ],
      zip_safe=False)

