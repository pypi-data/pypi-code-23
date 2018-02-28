# -*- coding: utf-8 -*-

"""APIs to measure performance in different scenarios.

A **scenario** is fully defined by a *scenario type* and all descriptors
returned by I/O handling procedures :py:mod:`.dataLoadStore` (reports apart).

The *scenario type* is basically something that - as of
current implementation - allows to distinguish among worst scenario,
best scenario and a normal/mean one. In fact, even with the same
descriptors, the actual arrangment of randomly generated values into the
sequences (e.g. inflation) heavily impacts on actual performances.

The set of descriptors
allows to carry out a fondo pensione as well as a TFR development plan
by running :py:func:`.engine.fondoPensione.getPiano` and
:py:func:`.engine.tfr.getPiano`. However descriptors by themselves as well as
a single plan development
procedure call aren't enough to appreciate the average performance of both
fondo pensione and TFR,
because some random characteristics are usually involved - that's to say
every call to functions above returns different results which hence cannot
be taken as performance measurement by their own.

This is where this module comes into play. It implements what's usually called
a *simulation*. By repeatedly calling procedures said above, code in this
module is able to compute average values for all metrics specified in
the report (:py:func:`.engine.report.get`) as well as how values themselves
are precise.

List of sub-packages
====================

.. autosummary::
   :toctree: _autosummary

   fpSim
   errors
"""
