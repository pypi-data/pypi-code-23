# -*- coding: utf-8 -*-

# Copyright © 2017
# Contributed by Raphaël Bleuse <raphael.bleuse@imag.fr>
#
# This file is part of procset.py, a pure python module to manage sets of
# closed intervals.
#
#   procset.py is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License version 3 only
#   as published by the Free Software Foundation.
#
#   procset.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License version 3 for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License version 3 along with this program.  If not, see
#   <https://www.gnu.org/licenses/>.

"""
Wrapper functions around procset to provide the API of interval_set.

This module aims at easing the transition from interval_set to procset, and
should not be used in any new project. The code is not optimized at all, as it
converts the structures to ProcSet back and forth.

The module is planned for removal in the next major release.
"""

import functools
import warnings

from procset import ProcSet


# helper decorator factory

def _deprecated(message=""):
    def _decorated(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            warnings.warn(
                message,
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return _wrapper
    return _decorated


# old API implementation: string conversions

@_deprecated("Deprecated function: use str(intervals) or format(intervals) instead.")
def interval_set_to_string(itvs, separator=" "):
    """[deprecated] Convert an intervals' set into a string."""
    format_spec = '-' + separator[0]
    return format(ProcSet(*itvs), format_spec)


@_deprecated("Deprecated function: use ProcSet.from_str(s) instead.")
def string_to_interval_set(string, separator=" "):
    """[deprecated] Transform a string to an intervals' set."""
    return list(ProcSet.from_str(string, outsep=separator).intervals())


# old API implementation: ID list conversions

@_deprecated("Deprecated function: use ProcSet(*ids) instead.")
def id_list_to_iterval_set(idlist):
    """[deprecated] Convert a list of ID (int) into an intervals' set."""
    return list(ProcSet(*idlist).intervals())


@_deprecated("Deprecated function: use list(itvs) instead.")
def interval_set_to_id_list(itvs):
    """[deprecated] Convert an intervals' set into a list of ID (int)."""
    return list(ProcSet(*itvs))


# old API implementation: ID set conversions

@_deprecated("Deprecated function: use set(itvs) instead.")
def interval_set_to_set(itvs):
    """[deprecated] Convert an intervals' set into a set of ID (int)."""
    return set(ProcSet(*itvs))


@_deprecated("Deprecated function: use ProcSet(*s) instead.")
def set_to_interval_set(idset):
    """[deprecated] Convert a set of ID (int) into an intervals' set."""
    return list(ProcSet(*idset).intervals())


# old API implementation: statistics

@_deprecated("Deprecated function: use len(itvs) instead.")
def total(itvs):
    """[deprecated] Compute the number of elements in the whole set."""
    return len(ProcSet(*itvs))


# old API implementation: set theory operations

@_deprecated("Deprecated function: use == instead.")
def equals(itvs1, itvs2):
    """[deprecated] Check for equality between two intervals' sets."""
    return ProcSet(*itvs1) == ProcSet(*itvs2)


@_deprecated("Deprecated function: itvs_base - itvs2 instead.")
def difference(itvs1, itvs2):
    """
    [deprecated] Return the intervals' set containing elements in the first set
    but not in the second.
    """
    return list((ProcSet(*itvs1) - ProcSet(*itvs2)).intervals())


@_deprecated("Deprecated function: use itvs1 & itvs2 instead.")
def intersection(itvs1, itvs2):
    """
    [deprecated] Return the intervals' set containing elements common to the
    first and second sets.
    """
    return list((ProcSet(*itvs1) & ProcSet(*itvs2)).intervals())


@_deprecated("Deprecated function: use itvs1 | itvs2 instead.")
def union(itvs1, itvs2):
    """
    [deprecated] Return the intervals' set with the elements from the first set
    and the second set.
    """
    return list((ProcSet(*itvs1) | ProcSet(*itvs2)).intervals())


@_deprecated("Deprecated function: use aggregate method instead.")
def aggregate(itvs):
    """
    [deprecated] Return the smallest interval containing all intervals from the
    given intervals' set.
    """
    return list(ProcSet(*itvs).aggregate().intervals())
