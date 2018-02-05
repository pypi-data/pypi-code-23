import sys
import os

execfile (os.path.abspath("../source/confcommon.py"))

# primary_domain = 'fortran'

# General information about the project.
project = u'CALCEPH  - Fortran 2003 language'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'calceph.tex', u'CALCEPH - Fortran 2003 language',
     u'M. Gastineau, J. Laskar, A. Fienga, H. Manche', 'manual'),
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'calceph', u'CALCEPH - Fortran 2003 language',
     author, 'calceph', 'CALCEPH - Fortran 2003 language.',
     'Miscellaneous'),
]

def setup(app):
    app.add_config_value('calcephapi', 'F2003', 'env')


rst_epilog = """
.. |API| replace:: Fortran 2003
.. |supportedspk| replace:: 1, 2, 3, 12, 13, 20, 102, 103 and 120
.. |LIBRARYNAME| replace:: CALCEPH Library
.. |LIBRARYSHORTNAME| replace:: CALCEPH
.. |EMAIL| replace:: inpop.imcce@obspm.fr
.. |eph| replace:: associated to *eph*
.. |ephemerisdescriptoreph| replace:: the ephemeris descriptor *eph*
.. |menu_calceph_open| replace:: calceph_open
.. |calceph_open| replace:: :f:func:`calceph_open()`
.. |menu_calceph_open_array| replace:: calceph_open_array
.. |calceph_open_array| replace:: :f:func:`calceph_open_array()`
.. |menu_calceph_close| replace:: calceph_close
.. |calceph_close| replace:: :f:func:`calceph_close()`
.. |menu_calceph_prefetch| replace:: calceph_prefetch
.. |calceph_prefetch| replace:: :f:func:`calceph_prefetch()`
.. |menu_calceph_compute| replace:: calceph_compute
.. |calceph_compute| replace:: :f:func:`calceph_compute()`
.. |menu_calceph_compute_unit| replace:: calceph_compute_unit
.. |calceph_compute_unit| replace:: :f:func:`calceph_compute_unit()`
.. |menu_calceph_getconstant| replace:: calceph_getconstant
.. |calceph_getconstant| replace:: :f:func:`calceph_getconstant()`
.. |menu_calceph_getconstantcount| replace:: calceph_getconstantcount
.. |calceph_getconstantcount| replace:: :f:func:`calceph_getconstantcount()`
.. |menu_calceph_getconstantindex| replace:: calceph_getconstantindex
.. |calceph_getconstantindex| replace:: :f:func:`calceph_getconstantindex()`
.. |menu_calceph_gettimescale| replace:: calceph_gettimescale
.. |calceph_gettimescale| replace:: :f:func:`calceph_gettimescale()`
.. |menu_calceph_gettimespan| replace:: calceph_gettimespan
.. |calceph_gettimespan| replace:: :f:func:`calceph_gettimespan()`
.. |menu_calceph_getpositionrecordcount| replace:: calceph_getpositionrecordcount
.. |calceph_getpositionrecordcount| replace:: :f:func:`calceph_getpositionrecordcount()`
.. |menu_calceph_getpositionrecordindex| replace:: calceph_getpositionrecordindex
.. |calceph_getpositionrecordindex| replace:: :f:func:`calceph_getpositionrecordindex()`
.. |menu_calceph_getorientrecordcount| replace:: calceph_getorientrecordcount
.. |calceph_getorientrecordcount| replace:: :f:func:`calceph_getorientrecordcount()`
.. |menu_calceph_getorientrecordindex| replace:: calceph_getorientrecordindex
.. |calceph_getorientrecordindex| replace:: :f:func:`calceph_getorientrecordindex()`
.. |menu_calceph_orient_unit| replace:: calceph_orient_unit
.. |calceph_orient_unit| replace:: :f:func:`calceph_orient_unit()`
.. |menu_calceph_rotangmom_unit| replace:: calceph_rotangmom_unit
.. |calceph_rotangmom_unit| replace:: :f:func:`calceph_rotangmom_unit()`
.. |menu_calceph_compute_order| replace:: calceph_compute_order
.. |calceph_compute_order| replace:: :f:func:`calceph_compute_order()`
.. |menu_calceph_orient_order| replace:: calceph_orient_order
.. |calceph_orient_order| replace:: :f:func:`calceph_orient_order()`
.. |menu_calceph_rotangmom_order| replace:: calceph_rotangmom_order
.. |calceph_rotangmom_order| replace:: :f:func:`calceph_rotangmom_order()`
.. |menu_calceph_sopen| replace:: calceph_sopen
.. |calceph_sopen| replace:: :f:func:`calceph_sopen()`
.. |menu_calceph_sclose| replace:: calceph_sclose
.. |calceph_sclose| replace:: :f:func:`calceph_sclose()`
.. |menu_calceph_scompute| replace:: calceph_scompute
.. |calceph_scompute| replace:: :f:func:`calceph_scompute()`
.. |menu_calceph_sgetconstant| replace:: calceph_sgetconstant
.. |calceph_sgetconstant| replace:: :f:func:`calceph_sgetconstant()`
.. |menu_calceph_sgetconstantcount| replace:: calceph_sgetconstantcount
.. |calceph_sgetconstantcount| replace:: :f:func:`calceph_sgetconstantcount()`
.. |menu_calceph_sgetconstantindex| replace:: calceph_sgetconstantindex
.. |calceph_sgetconstantindex| replace:: :f:func:`calceph_sgetconstantindex()`
.. |menu_calceph_sgettimescale| replace:: calceph_sgettimescale
.. |calceph_sgettimescale| replace:: :f:func:`calceph_sgettimescale()`
.. |menu_calceph_sgettimespan| replace:: calceph_sgettimespan
.. |calceph_sgettimespan| replace:: :f:func:`calceph_sgettimespan()`
.. |menu_calceph_seterrorhandler| replace:: calceph_seterrorhandler
.. |calceph_seterrorhandler| replace:: :f:func:`calceph_seterrorhandler()`
.. |menu_calceph_getversion_str| replace:: calceph_getversion_str
.. |menu_Headers_and_Libraries| replace:: Modules and Libraries
.. |CALCEPH_UNIT_AU| replace:: :f:var:`CALCEPH_UNIT_AU`
.. |CALCEPH_UNIT_KM| replace:: :f:var:`CALCEPH_UNIT_KM`
.. |CALCEPH_UNIT_DAY| replace:: :f:var:`CALCEPH_UNIT_DAY`
.. |CALCEPH_UNIT_SEC| replace:: :f:var:`CALCEPH_UNIT_SEC`
.. |CALCEPH_UNIT_RAD| replace:: :f:var:`CALCEPH_UNIT_RAD`
.. |CALCEPH_USE_NAIFID| replace:: :f:var:`CALCEPH_USE_NAIFID`
.. |retfuncfails0| replace::  0 if an error occurs, otherwise non-zero value.
.. |funcfails0| replace::  On exit, it returns 0 if an error occurs, otherwise the return value is a non-zero value.
.. |retfuncfailsNULL| replace::  This value is C_NULL_PTR if an error occurs, otherwise non-C_NULL_PTR value.
.. |funcfailsNULL| replace:: On exit, it returns C_NULL_PTR if an error occurs, otherwise the return value is a non-C_NULL_PTR value.
"""

highlight_language = 'fortran'

