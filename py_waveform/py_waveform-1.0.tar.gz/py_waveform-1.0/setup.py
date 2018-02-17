from setuptools import setup, Extension

module = Extension("waveform", sources=["waveform.c"], libraries=['groove'])

setup(name="py_waveform",
      version="1.0",
      description="This package is for waveform generation of the given audio file.",
      author='Basit Raza',
      author_email='basit.raza11@gmail.com',
      license='MIT',
      url='https://github.com/geek96/waveform-python',
      ext_modules=[module])
