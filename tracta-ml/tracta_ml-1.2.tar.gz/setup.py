from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

cmdclass = { }
ext_modules = [ ]

if True:
    ext_modules += [
        Extension("tracta_ml.evolve", [ "tracta_ml/cython/evolve.pyx" ]),
        Extension("tracta_ml.genetic_operators", ["tracta_ml/cython/genetic_operators.pyx"]),
        Extension("tracta_ml.model_optimizer", ["tracta_ml/cython/model_optimizer.pyx"]),
        Extension("tracta_ml.pool_maintenance", ["tracta_ml/cython/pool_maintenance.pyx"]),
    ]
    cmdclass.update({ 'build_ext': build_ext })

setup(name='tracta_ml',
      version='1.2',
      description='Combined hyper-parameter optimization and feature selection\
      for machine learning models using micro genetic algorithms',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
      ],
      url='https://github.com/SankethNagarajan/tracta_ml',
      author='Sanketh Nagarajan',
      author_email='sanketh.objml@gmail.com',
      license='BSD 3-Clause "New" or "Revised" License',
      packages=['tracta_ml'],
      cmdclass=cmdclass,
      ext_modules=ext_modules,
      install_requires=['sklearn', 'numpy', 'pandas',\
                        'datetime','matplotlib',
                        ],
      zip_safe=False)