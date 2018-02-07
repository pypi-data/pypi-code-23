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

"""
SGRT folder and file name definition.

"""

from datetime import datetime
from collections import OrderedDict

from geopathfinder.folder_naming import SmartPath
from geopathfinder.file_naming import SmartFilename


class SgrtFilename(SmartFilename):

    """
    SGRT file name definition using SmartFilename class.
    """

    def __init__(self, fields):

        self.date_format = "%Y%m%d_%H%M%S"

        fields_def = OrderedDict(
            [('pflag', 1), ('start_time', 15), ('end_time', 15),
             ('var_name', 9), ('sensor_id', 3), ('mode_id', 2),
             ('product_type', 3), ('res_class', 1), ('level', 1),
             ('pol', 2), ('direction', 4), ('relative_orbit', 4),
             ('workflow_id', 5), ('ftile_name', 3)])

        for v in ['start_time', 'end_time']:
            if v in fields:
                fields[v] = fields[v].strftime(self.date_format)

        super(SgrtFilename, self).__init__(fields, fields_def, ext='.tif')

    def __getitem__(self, key):
        """
        Get field content.

        Parameters
        ----------
        key : str
            Field name.

        Returns
        -------
        item : str
            Item value.
        """
        item = super(SgrtFilename, self).__getitem__(key)

        if key in ['start_time', 'end_time']:
            item = datetime.strptime(item, self.date_format)

        return item

    def __setitem__(self, key, value):
        """
        Set field content.

        Parameters
        ----------
        key : str
            Field name.
        value : str or datetime
            Field value.
        """
        if key in ['start_time', 'end_time'] and isinstance(value, datetime):
            value = value.strftime(self.date_format)

        super(SgrtFilename, self).__setitem__(key, value)



def full_sgrt_tree(root, sensor=None, mode=None, group=None, datalog=None,
                   product=None, wflow=None, grid=None, tile=None, var=None,
                   qlook=True, make_dir=False):
    '''
    Realisation of the full SGRT folder naming convention, yielding a single
    SmartPath.

    Parameters
    ----------
    root : str
    sensor : str
    mode : str
    group : str
    datalog : str
    product : str
    wflow : str
    grid : str
    tile : str
    var : str
    qlook : bool
    make_dir : bool

    Returns
    -------
    SmartPath
        Object for the path
    '''

    # defining the folder levels
    levels = {'root': root, 'sensor': sensor, 'mode': mode, 'group': group,
              'datalog': datalog, 'product': product, 'wflow': wflow,
              'grid': grid, 'tile': tile, 'var': var, 'qlook': 'qlooks'}

    # defining the hierarchy
    hierarchy = ['root', 'sensor', 'mode', 'group',
                 'datalog', 'product', 'wflow', 'grid',
                 'tile', 'var', 'qlook']

    return SmartPath(levels, hierarchy, make_dir=make_dir)


if __name__ == '__main__':
    pass
