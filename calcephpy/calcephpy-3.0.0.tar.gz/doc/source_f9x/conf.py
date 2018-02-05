import sys
import os

execfile (os.path.abspath("../source/confcommon.py"))

# primary_domain = 'fortran'

# General information about the project.
project = u'CALCEPH  - Fortran 77/90/95 language'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'calceph.tex', u'CALCEPH - Fortran 77/90/95 language',
     u'M. Gastineau, J. Laskar, A. Fienga, H. Manche', 'manual'),
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'calceph', u'CALCEPH - Fortran 77/90/95 language',
     author, 'calceph', 'CALCEPH - Fortran 77/90/95 language.',
     'Miscellaneous'),
]


def setup(app):
    app.add_config_value('calcephapi', 'F90', 'env')


rst_epilog = """
.. |API| replace:: Fortran 77/90/95
.. |supportedspk| replace:: 1, 2, 3, 12, 13, 20, 102, 103 and 120
.. |LIBRARYNAME| replace:: CALCEPH Library
.. |LIBRARYSHORTNAME| replace:: CALCEPH
.. |EMAIL| replace:: inpop.imcce@obspm.fr
.. |eph| replace:: associated to *eph*
.. |ephemerisdescriptoreph| replace:: the ephemeris descriptor *eph*
.. |menu_calceph_open| replace:: calceph_open
.. |calceph_open| replace:: :f:func:`f90calceph_open()`
.. |menu_calceph_open_array| replace:: f90calceph_open_array
.. |calceph_open_array| replace:: :f:func:`f90calceph_open_array()`
.. |menu_calceph_close| replace:: f90calceph_close
.. |calceph_close| replace:: :f:func:`f90calceph_close()`
.. |menu_calceph_prefetch| replace:: f90calceph_prefetch
.. |calceph_prefetch| replace:: :f:func:`f90calceph_prefetch()`
.. |menu_calceph_compute| replace:: f90calceph_compute
.. |calceph_compute| replace:: :f:func:`f90calceph_compute()`
.. |menu_calceph_compute_unit| replace:: f90calceph_compute_unit
.. |calceph_compute_unit| replace:: :f:func:`f90calceph_compute_unit()`
.. |menu_calceph_getconstant| replace:: f90calceph_getconstant
.. |calceph_getconstant| replace:: :f:func:`f90calceph_getconstant()`
.. |menu_calceph_getconstantcount| replace:: f90calceph_getconstantcount
.. |calceph_getconstantcount| replace:: :f:func:`f90calceph_getconstantcount()`
.. |menu_calceph_getconstantindex| replace:: f90calceph_getconstantindex
.. |calceph_getconstantindex| replace:: :f:func:`f90calceph_getconstantindex()`
.. |menu_calceph_gettimescale| replace:: f90calceph_gettimescale
.. |calceph_gettimescale| replace:: :f:func:`f90calceph_gettimescale()`
.. |menu_calceph_gettimespan| replace:: f90calceph_gettimespan
.. |calceph_gettimespan| replace:: :f:func:`f90calceph_gettimespan()`
.. |menu_calceph_getpositionrecordcount| replace:: f90calceph_getpositionrecordcount
.. |calceph_getpositionrecordcount| replace:: :f:func:`f90calceph_getpositionrecordcount()`
.. |menu_calceph_getpositionrecordindex| replace:: f90calceph_getpositionrecordindex
.. |calceph_getpositionrecordindex| replace:: :f:func:`f90calceph_getpositionrecordindex()`
.. |menu_calceph_getorientrecordcount| replace:: f90calceph_getorientrecordcount
.. |calceph_getorientrecordcount| replace:: :f:func:`f90calceph_getorientrecordcount()`
.. |menu_calceph_getorientrecordindex| replace:: f90calceph_getorientrecordindex
.. |calceph_getorientrecordindex| replace:: :f:func:`f90calceph_getorientrecordindex()`
.. |menu_calceph_orient_unit| replace:: f90calceph_orient_unit
.. |calceph_orient_unit| replace:: :f:func:`f90calceph_orient_unit()`
.. |menu_calceph_rotangmom_unit| replace:: f90calceph_rotangmom_unit
.. |calceph_rotangmom_unit| replace:: :f:func:`f90calceph_rotangmom_unit()`
.. |menu_calceph_compute_order| replace:: f90calceph_compute_order
.. |calceph_compute_order| replace:: :f:func:`f90calceph_compute_order()`
.. |menu_calceph_orient_order| replace:: f90calceph_orient_order
.. |calceph_orient_order| replace:: :f:func:`f90calceph_orient_order()`
.. |menu_calceph_rotangmom_order| replace:: f90calceph_rotangmom_order
.. |calceph_rotangmom_order| replace:: :f:func:`f90calceph_rotangmom_order()`
.. |menu_calceph_sopen| replace:: f90calceph_sopen
.. |calceph_sopen| replace:: :f:func:`f90calceph_sopen()`
.. |menu_calceph_sclose| replace:: f90calceph_sclose
.. |calceph_sclose| replace:: :f:func:`f90calceph_sclose()`
.. |menu_calceph_scompute| replace:: f90calceph_scompute
.. |calceph_scompute| replace:: :f:func:`f90calceph_scompute()`
.. |menu_calceph_sgetconstant| replace:: f90calceph_sgetconstant
.. |calceph_sgetconstant| replace:: :f:func:`f90calceph_sgetconstant()`
.. |menu_calceph_sgetconstantcount| replace:: f90calceph_sgetconstantcount
.. |calceph_sgetconstantcount| replace:: :f:func:`f90calceph_sgetconstantcount()`
.. |menu_calceph_sgetconstantindex| replace:: f90calceph_sgetconstantindex
.. |calceph_sgetconstantindex| replace:: :f:func:`f90calceph_sgetconstantindex()`
.. |menu_calceph_sgettimescale| replace:: f90calceph_sgettimescale
.. |calceph_sgettimescale| replace:: :f:func:`f90calceph_sgettimescale()`
.. |menu_calceph_sgettimespan| replace:: f90calceph_sgettimespan
.. |calceph_sgettimespan| replace:: :f:func:`f90calceph_sgettimespan()`
.. |menu_calceph_seterrorhandler| replace:: f90calceph_seterrorhandler
.. |calceph_seterrorhandler| replace:: :f:func:`f90calceph_seterrorhandler()`
.. |menu_calceph_getversion_str| replace:: f90calceph_getversion_str
.. |menu_Headers_and_Libraries| replace:: Headers and Libraries
.. |CALCEPH_UNIT_AU| replace:: :f:var:`CALCEPH_UNIT_AU`
.. |CALCEPH_UNIT_KM| replace:: :f:var:`CALCEPH_UNIT_KM`
.. |CALCEPH_UNIT_DAY| replace:: :f:var:`CALCEPH_UNIT_DAY`
.. |CALCEPH_UNIT_SEC| replace:: :f:var:`CALCEPH_UNIT_SEC`
.. |CALCEPH_UNIT_RAD| replace:: :f:var:`CALCEPH_UNIT_RAD`
.. |CALCEPH_USE_NAIFID| replace:: :f:var:`CALCEPH_USE_NAIFID`
.. |retfuncfails0| replace::  0 if an error occurs, otherwise non-zero value.
.. |funcfails0| replace::  On exit, it returns 0 if an error occurs, otherwise the return value is a non-zero value.
.. |retfuncfailsNULL| replace::  0 if an error occurs, otherwise non-zero value.
.. |funcfailsNULL| replace:: On exit, it returns 0 if an error occurs, otherwise the return value is a non-zero value.
"""

highlight_language = 'fortran'

