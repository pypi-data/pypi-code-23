# setup.py

from distutils.core import setup
import os


setup(
    name='magnetmatter',
    version='0.2.1',
    packages=['magnetmatter',
      os.path.join('magnetmatter','modules'),
      os.path.join('magnetmatter','modules', '_plot_prf'),
      os.path.join('magnetmatter','modules','_plot_seq'),
      ],
    license='MIT',
    author='Pelle Garbus',
    author_email='garbus@inano.au.dk',
    description='Visualization of FullProf-refined neutron and X-ray powder diffraction data',
    long_description=open('README.txt').read(),
    install_requires=["numpy","pandas","matplotlib"],
    url = 'https://github.com/pgarbus/magnetmatter',
)
