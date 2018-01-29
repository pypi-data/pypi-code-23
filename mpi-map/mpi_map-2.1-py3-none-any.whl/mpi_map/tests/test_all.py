#
# This file is part of mpi_map.
#
# mpi_map is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mpi_map is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with mpi_map.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

import logging
import unittest

def run_all(log_level=logging.WARNING):
    from mpi_map.tests import test_pool

    logging.basicConfig(level=log_level)

    suites_list = [test_pool.build_suite() ]
    all_suites = unittest.TestSuite( suites_list )
    # Run
    tr = unittest.TextTestRunner(verbosity=2).run(all_suites)
    # Exit with error if fail
    nerr = len(tr.errors)
    nfail = len(tr.failures)
    if nerr + nfail > 0:
        print("Errors: %d, Failures: %d" % (nerr, nfail))
        sys.exit(1)

if __name__ == '__main__':
    run_all()