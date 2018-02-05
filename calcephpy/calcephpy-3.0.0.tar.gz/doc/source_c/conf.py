import sys
import os

execfile (os.path.abspath("../source/confcommon.py"))

primary_domain = 'c'

# General information about the project.
project = u'CALCEPH  - C language'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'calceph.tex', u'CALCEPH - C language',
     u'M. Gastineau, J. Laskar, A. Fienga, H. Manche', 'manual'),
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'calceph', u'CALCEPH - C language',
     author, 'calceph', 'CALCEPH - C language.',
     'Miscellaneous'),
]

def setup(app):
    app.add_config_value('calcephapi', 'C', 'env')


rst_epilog = """
.. |API| replace:: C
.. |supportedspk| replace:: 1, 2, 3, 12, 13, 20, 102, 103 and 120
.. |LIBRARYNAME| replace:: CALCEPH Library
.. |LIBRARYSHORTNAME| replace:: CALCEPH
.. |EMAIL| replace:: inpop.imcce@obspm.fr
.. |eph| replace:: associated to *eph*
.. |ephemerisdescriptoreph| replace:: the ephemeris descriptor *eph*
.. |menu_calceph_open| replace:: calceph_open
.. |calceph_open| replace:: :c:func:`calceph_open()`
.. |menu_calceph_open_array| replace:: calceph_open_array
.. |calceph_open_array| replace:: :c:func:`calceph_open_array()`
.. |menu_calceph_close| replace:: calceph_close
.. |calceph_close| replace:: :c:func:`calceph_close()`
.. |menu_calceph_prefetch| replace:: calceph_prefetch
.. |calceph_prefetch| replace:: :c:func:`calceph_prefetch()`
.. |menu_calceph_compute| replace:: calceph_compute
.. |calceph_compute| replace:: :c:func:`calceph_compute()`
.. |menu_calceph_compute_unit| replace:: calceph_compute_unit
.. |calceph_compute_unit| replace:: :c:func:`calceph_compute_unit()`
.. |menu_calceph_getconstant| replace:: calceph_getconstant
.. |calceph_getconstant| replace:: :c:func:`calceph_getconstant()`
.. |menu_calceph_getconstantcount| replace:: calceph_getconstantcount
.. |calceph_getconstantcount| replace:: :c:func:`calceph_getconstantcount()`
.. |menu_calceph_getconstantindex| replace:: calceph_getconstantindex
.. |calceph_getconstantindex| replace:: :c:func:`calceph_getconstantindex()`
.. |menu_calceph_gettimescale| replace:: calceph_gettimescale
.. |calceph_gettimescale| replace:: :f:func:`calceph_gettimescale()`
.. |menu_calceph_gettimespan| replace:: calceph_gettimespan
.. |calceph_gettimespan| replace:: :c:func:`calceph_gettimespan()`
.. |menu_calceph_getpositionrecordcount| replace:: calceph_getpositionrecordcount
.. |calceph_getpositionrecordcount| replace:: :c:func:`calceph_getpositionrecordcount()`
.. |menu_calceph_getpositionrecordindex| replace:: calceph_getpositionrecordindex
.. |calceph_getpositionrecordindex| replace:: :c:func:`calceph_getpositionrecordindex()`
.. |menu_calceph_getorientrecordcount| replace:: calceph_getorientrecordcount
.. |calceph_getorientrecordcount| replace:: :c:func:`calceph_getorientrecordcount()`
.. |menu_calceph_getorientrecordindex| replace:: calceph_getorientrecordindex
.. |calceph_getorientrecordindex| replace:: :c:func:`calceph_getorientrecordindex()`
.. |menu_calceph_orient_unit| replace:: calceph_orient_unit
.. |calceph_orient_unit| replace:: :c:func:`calceph_orient_unit()`
.. |menu_calceph_rotangmom_unit| replace:: calceph_rotangmom_unit
.. |calceph_rotangmom_unit| replace:: :c:func:`calceph_rotangmom_unit()`
.. |menu_calceph_compute_order| replace:: calceph_compute_order
.. |calceph_compute_order| replace:: :c:func:`calceph_compute_order()`
.. |menu_calceph_orient_order| replace:: calceph_orient_order
.. |calceph_orient_order| replace:: :c:func:`calceph_orient_order()`
.. |menu_calceph_rotangmom_order| replace:: calceph_rotangmom_order
.. |calceph_rotangmom_order| replace:: :c:func:`calceph_rotangmom_order()`
.. |menu_calceph_sopen| replace:: calceph_sopen
.. |calceph_sopen| replace:: :c:func:`calceph_sopen()`
.. |menu_calceph_sclose| replace:: calceph_sclose
.. |calceph_sclose| replace:: :c:func:`calceph_sclose()`
.. |menu_calceph_scompute| replace:: calceph_scompute
.. |calceph_scompute| replace:: :c:func:`calceph_scompute()`
.. |menu_calceph_sgetconstant| replace:: calceph_sgetconstant
.. |calceph_sgetconstant| replace:: :c:func:`calceph_sgetconstant()`
.. |menu_calceph_sgetconstantcount| replace:: calceph_sgetconstantcount
.. |calceph_sgetconstantcount| replace:: :c:func:`calceph_sgetconstantcount()`
.. |menu_calceph_sgetconstantindex| replace:: calceph_sgetconstantindex
.. |calceph_sgetconstantindex| replace:: :c:func:`calceph_sgetconstantindex()`
.. |menu_calceph_sgettimescale| replace:: calceph_sgettimescale
.. |calceph_sgettimescale| replace:: :c:func:`calceph_sgettimescale()`
.. |menu_calceph_sgettimespan| replace:: calceph_sgettimespan
.. |calceph_sgettimespan| replace:: :c:func:`calceph_sgettimespan()`
.. |menu_calceph_seterrorhandler| replace:: calceph_seterrorhandler
.. |calceph_seterrorhandler| replace:: :c:func:`calceph_seterrorhandler()`
.. |menu_calceph_getversion_str| replace:: calceph_getversion_str
.. |menu_Headers_and_Libraries| replace:: Headers and Libraries
.. |CALCEPH_UNIT_AU| replace:: :c:macro:`CALCEPH_UNIT_AU`
.. |CALCEPH_UNIT_KM| replace:: :c:macro:`CALCEPH_UNIT_KM`
.. |CALCEPH_UNIT_DAY| replace:: :c:macro:`CALCEPH_UNIT_DAY`
.. |CALCEPH_UNIT_SEC| replace:: :c:macro:`CALCEPH_UNIT_SEC`
.. |CALCEPH_UNIT_RAD| replace:: :c:macro:`CALCEPH_UNIT_RAD`
.. |CALCEPH_USE_NAIFID| replace:: :c:macro:`CALCEPH_USE_NAIFID`
.. |retfuncfails0| replace::  0 if an error occurs, otherwise non-zero value.
.. |funcfails0| replace::  On exit, it returns 0 if an error occurs, otherwise the return value is a non-zero value.
.. |retfuncfailsNULL| replace::  This value is NULL if an error occurs, otherwise non-NULL value.
.. |funcfailsNULL| replace:: On exit, it returns NULL if an error occurs, otherwise the return value is a non-NULL value.
"""

highlight_language = 'C'

