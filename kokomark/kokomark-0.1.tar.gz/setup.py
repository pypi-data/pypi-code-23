from setuptools import setup

setup(name='kokomark',
      version='0.1',
      description='Library for watermarking images. Used for 3.4.56.7 @ ece.ntua.gr',
      url='https://github.com/elikatsis/kokomrk',
      author='Nikos Kormpakis',
      author_email='el10785@mail.ntua.gr',
      license='MIT',
      packages=['kokomark'],
      zip_safe=False,
      python_requires=">=3.5",
      install_requires=['Pillow==5.0.0']
)
