import setuptools
import io

setuptools.setup(setup_requires=['pbr'], pbr=True)

with io.open('README.rst', encoding="utf-8") as f:
    long_description = f.read()
