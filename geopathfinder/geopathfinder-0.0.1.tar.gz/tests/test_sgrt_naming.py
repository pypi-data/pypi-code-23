# Copyright (c) 2018, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



import unittest
from datetime import datetime

import logging

from geopathfinder.sgrt_naming import SgrtFilename

logging.basicConfig(level=logging.INFO)


class TestSgrtFilename(unittest.TestCase):

    def setUp(self):
        self.start_time = datetime(2008, 1, 1, 12, 23, 33)
        self.end_time = datetime(2008, 1, 1, 13, 23, 33)

        fields = {'start_time': self.start_time, 'end_time': self.end_time,
                  'var_name': 'SSM'}

        self.sgrt_fn = SgrtFilename(fields)

    def test_build_sgrt_filename(self):
        """
        Test building SGRT file name.
        """
        fn = ('-_20080101_122333_20080101_132333_------SSM_---_--_---_-_-_--_'
              '----_----_-----_---.tif')

        self.assertEqual(self.sgrt_fn.__repr__(), fn)

    def test_set_and_get_datetime(self):
        """
        Test set and get start and end time.
        """
        self.assertEqual(self.sgrt_fn['start_time'], self.start_time)
        self.assertEqual(self.sgrt_fn['end_time'], self.end_time)

        new_start_time = datetime(2009, 1, 1, 12, 23, 33)
        self.sgrt_fn['start_time'] = new_start_time

        self.assertEqual(self.sgrt_fn['start_time'], new_start_time)


if __name__ == "__main__":
    unittest.main()
