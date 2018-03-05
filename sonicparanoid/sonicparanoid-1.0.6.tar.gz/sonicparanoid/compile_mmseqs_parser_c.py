from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules = cythonize('mmseqs_parser_c.pyx', compiler_directives={'language_level': 3}))
