from setuptools import setup

setup(name='scatteringmatrix',
      version='0.1.0.dev3',
      description='Optical scattering matrix library',
      author='Andrew G. Flood',
      author_email='andrew.flood@mail.utoronto.ca',
      license='MIT',
      classifiers=[
              'Development Status :: 2 - Pre-Alpha',
              'Intended Audience :: Science/Research',
              'Topic :: Scientific/Engineering',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.2',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',
              ],
      keywords='optics scattering matrix photonics',
      packages=[],
      py_modules=["scatteringmatrix"],
      install_requires=['numpy','scipy'],
      python_requires='>=3',
      zip_safe=False)