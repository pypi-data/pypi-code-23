
import sys
import os

execfile (os.path.abspath("../source/confcommon.py"))

primary_domain = 'py'

# General information about the project.
project = u'CALCEPH  - Python language'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = [ 'condsingle' ]


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'calceph.tex', u'CALCEPH - Python language',
     u'M. Gastineau, J. Laskar, A. Fienga, H. Manche', 'manual'),
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'calceph', u'CALCEPH - Python language',
     author, 'calceph', 'CALCEPH - Python language.',
     'Miscellaneous'),
]


def setup(app):
    app.add_config_value('calcephapi', 'Python', 'env')

rst_epilog = """
.. |API| replace:: Python
.. |supportedspk| replace:: 1, 2, 3, 12, 13, 20, 102, 103 and 120
.. |LIBRARYNAME| replace:: CALCEPH Library
.. |LIBRARYSHORTNAME| replace:: CALCEPH
.. |EMAIL| replace:: inpop.imcce@obspm.fr
.. |eph| replace:: *self*
.. |ephemerisdescriptoreph| replace:: the ephemeris descriptor 
.. |menu_calceph_open| replace:: calcephpy.CalcephBin.open
.. |calceph_open| replace:: :py:func:`calcephpy.CalcephBin.open()`
.. |menu_calceph_open_array| replace:: calcephpy.CalcephBin.open_array
.. |calceph_open_array| replace:: :py:func:`calcephpy.CalcephBin.open_array()`
.. |menu_calceph_close| replace:: calcephpy.CalcephBin.close
.. |calceph_close| replace:: :py:func:`calcephpy.CalcephBin.close()`
.. |menu_calceph_prefetch| replace:: calcephpy.CalcephBin.prefetch
.. |calceph_prefetch| replace:: :py:func:`calcephpy.CalcephBin.prefetch()`
.. |menu_calceph_compute| replace:: calcephpy.CalcephBin.compute
.. |calceph_compute| replace:: :py:func:`calcephpy.CalcephBin.compute()`
.. |menu_calceph_compute_unit| replace:: calcephpy.CalcephBin.compute_unit
.. |calceph_compute_unit| replace:: :py:func:`calcephpy.CalcephBin.compute_unit()`
.. |menu_calceph_getconstant| replace:: calcephpy.CalcephBin.getconstant
.. |calceph_getconstant| replace:: :py:func:`calcephpy.CalcephBin.getconstant()`
.. |menu_calceph_getconstantcount| replace:: calcephpy.CalcephBin.getconstantcount
.. |calceph_getconstantcount| replace:: :py:func:`calcephpy.CalcephBin.getconstantcount()`
.. |menu_calceph_getconstantindex| replace:: calcephpy.CalcephBin.getconstantindex
.. |calceph_getconstantindex| replace:: :py:func:`calcephpy.CalcephBin.getconstantindex()`
.. |menu_calceph_gettimescale| replace:: calcephpy.CalcephBin.gettimescale
.. |calceph_gettimescale| replace:: :py:func:`calcephpy.CalcephBin.gettimescale()`
.. |menu_calceph_gettimespan| replace:: calcephpy.CalcephBin.gettimespan
.. |calceph_gettimespan| replace:: :py:func:`calcephpy.CalcephBin.gettimespan()`
.. |menu_calceph_getpositionrecordcount| replace:: calcephpy.CalcephBin.getpositionrecordcount
.. |calceph_getpositionrecordcount| replace:: :py:func:`calcephpy.CalcephBin.getpositionrecordcount()`
.. |menu_calceph_getpositionrecordindex| replace:: calcephpy.CalcephBin.getpositionrecordindex
.. |calceph_getpositionrecordindex| replace:: :py:func:`calcephpy.CalcephBin.getpositionrecordindex()`
.. |menu_calceph_getorientrecordcount| replace:: calcephpy.CalcephBin.getorientrecordcount
.. |calceph_getorientrecordcount| replace:: :py:func:`calcephpy.CalcephBin.getorientrecordcount()`
.. |menu_calceph_getorientrecordindex| replace:: calcephpy.CalcephBin.getorientrecordindex
.. |calceph_getorientrecordindex| replace:: :py:func:`calcephpy.CalcephBin.getorientrecordindex()`
.. |menu_calceph_orient_unit| replace:: calcephpy.CalcephBin.orient_unit
.. |calceph_orient_unit| replace:: :py:func:`calcephpy.CalcephBin.orient_unit()`
.. |menu_calceph_rotangmom_unit| replace:: calcephpy.CalcephBin.rotangmom_unit
.. |calceph_rotangmom_unit| replace:: :py:func:`calcephpy.CalcephBin.rotangmom_unit()`
.. |menu_calceph_compute_order| replace:: calcephpy.CalcephBin.compute_order
.. |calceph_compute_order| replace:: :py:func:`calcephpy.CalcephBin.compute_order()`
.. |menu_calceph_orient_order| replace:: calcephpy.CalcephBin.orient_order
.. |calceph_orient_order| replace:: :py:func:`calcephpy.CalcephBin.orient_order()`
.. |menu_calceph_rotangmom_order| replace:: calcephpy.CalcephBin.rotangmom_order
.. |calceph_rotangmom_order| replace:: :py:func:`calcephpy.CalcephBin.rotangmom_order()`
.. |menu_calceph_sopen| replace:: calcephpy.CalcephBin.sopen
.. |calceph_sopen| replace:: :py:func:`calcephpy.CalcephBin.sopen()`
.. |menu_calceph_sclose| replace:: calcephpy.CalcephBin.sclose
.. |calceph_sclose| replace:: :py:func:`calcephpy.CalcephBin.sclose()`
.. |menu_calceph_scompute| replace:: calcephpy.CalcephBin.scompute
.. |calceph_scompute| replace:: :py:func:`calcephpy.CalcephBin.scompute()`
.. |menu_calceph_sgetconstant| replace:: calcephpy.CalcephBin.sgetconstant
.. |calceph_sgetconstant| replace:: :py:func:`calcephpy.CalcephBin.sgetconstant()`
.. |menu_calceph_sgetconstantcount| replace:: calcephpy.CalcephBin.sgetconstantcount
.. |calceph_sgetconstantcount| replace:: :py:func:`calcephpy.CalcephBin.sgetconstantcount()`
.. |menu_calceph_sgetconstantindex| replace:: calcephpy.CalcephBin.sgetconstantindex
.. |calceph_sgetconstantindex| replace:: :py:func:`calcephpy.CalcephBin.sgetconstantindex()`
.. |menu_calceph_seterrorhandler| replace:: calcephpy.seterrorhandler
.. |calceph_seterrorhandler| replace:: :py:func:`calcephpy.seterrorhandler()`
.. |menu_calceph_getversion_str| replace:: calcephpy.getversion_str
.. |menu_Headers_and_Libraries| replace:: Modules
.. |CALCEPH_UNIT_AU| replace:: :py:data:`UNIT_AU`
.. |CALCEPH_UNIT_KM| replace:: :py:data:`UNIT_KM`
.. |CALCEPH_UNIT_DAY| replace:: :py:data:`UNIT_DAY`
.. |CALCEPH_UNIT_SEC| replace:: :py:data:`UNIT_SEC`
.. |CALCEPH_UNIT_RAD| replace:: :py:data:`UNIT_RAD`
.. |CALCEPH_USE_NAIFID| replace:: :py:data:`USE_NAIFID`
.. |retfuncfails0| replace:: returns 0 or an exception if an error occurs, otherwise a non-zero value.
.. |funcfails0| replace::  On exit, it returns 0 or an exception if an error occurs, otherwise the return value is a non-zero value.
.. |retfuncfailsNULL| replace:: raises an exception if an error occurs, otherwise a valid object.
.. |funcfailsNULL| replace:: On exit, it raises an exception if an error occurs, otherwise the return value is a valid value.
"""    

