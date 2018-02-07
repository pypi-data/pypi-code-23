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
import os
import shutil
import pandas as pd

from geopathfinder.folder_naming import SmartPath
from geopathfinder.folder_naming import extract_times

from geopathfinder.folder_naming import SmartTree

def cur_path():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


def get_test_sp(root,
                sensor=None,
                mode=None,
                group=None,
                datalog=None,
                product=None,
                wflow=None,
                grid=None,
                tile=None,
                var=None,
                qlook=True,
                make_dir=False):
    '''
    Function creating a SmartPath() for testing SmartPath().
    '''


    # defining the levels in the directory tree (order could become shuffled around)
    levels = {'root': root,
              'sensor': sensor,
              'mode': mode,
              'group': group,
              'datalog': datalog,
              'product': product,
              'wflow': wflow,
              'grid': grid,
              'tile': tile,
              'var': var,
              'qlook': 'qlooks'}

    # defining the hierarchy
    hierarchy = ['root', 'sensor', 'mode', 'group',
                 'datalog', 'product', 'wflow', 'grid',
                 'tile', 'var', 'qlook']

    return SmartPath(levels, hierarchy, make_dir=make_dir)


def get_test_sp_4_smarttree(sensor=None,
                mode=None,
                group=None,
                datalog=None,
                product=None,
                wflow=None,
                grid=None,
                tile=None,
                var=None,
                qlook=True,
                make_dir=False):
    '''
    Function creating a SmartPath() for testing SmartTree().
    '''


    # defining the levels in the directory tree (order could become shuffled around)
    levels = {'sensor': sensor,
              'mode': mode,
              'group': group,
              'datalog': datalog,
              'product': product,
              'wflow': wflow,
              'grid': grid,
              'tile': tile,
              'var': var,
              'qlook': 'qlooks'}

    # defining the hierarchy
    hierarchy = ['sensor', 'mode', 'group',
                 'datalog', 'product', 'wflow', 'grid',
                 'tile', 'var', 'qlook']

    return SmartPath(levels, hierarchy, make_dir=make_dir)


class TestSmartPath(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(cur_path(), 'test_temp_dir')
        self.sp_obj = get_test_sp(self.path, sensor='Sentinel-1_CSAR',
                                  mode='IWGRDH', group='products',
                                  datalog='datasets', product='ssm',
                                  wflow='C1003', grid='EQUI7_EU500M',
                                  tile='E048N012T6', var='ssm',
                                  make_dir=True)

    def tearDown(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)


    def test_get_dir(self):
        '''
        Testing the creation of the directory.
        '''

        result = self.sp_obj.get_dir(make_dir=True)

        assert os.path.exists(result)


    def test_build_levels(self):
        '''
        Testing the level creation.
        '''

        should = os.path.join(self.path, 'Sentinel-1_CSAR', 'IWGRDH', 'products',
                              'datasets', 'ssm', 'C1003')

        result = self.sp_obj.build_levels(level='wflow', make_dir=True)

        assert should == result

        assert os.path.exists(result)


    def test_get_level(self):
        '''
        Testing the level query.
        '''

        should = os.path.join(self.path, 'Sentinel-1_CSAR', 'IWGRDH')

        result = self.sp_obj['mode']

        assert should == result


    def test_expand_full_path(self):
        '''
        Testing the path expansion
        '''

        should = [os.path.join(self.path, 'Sentinel-1_CSAR', 'IWGRDH', 'MY_TEST.txt')]

        result = self.sp_obj.expand_full_path('mode', ['MY_TEST.txt'])

        assert should == result


    def test_search_files(self):
        '''
        Testing the file search yielding file lists.
        '''

        should = ['M20161218_051642--_SSM------_S1BIWGRDH1VVD_095_C1003_EU500M_E048N012T6.tif',
                  'M20170406_050911--_SSM------_S1AIWGRDH1VVD_022_C1003_EU500M_E048N012T6.tif']

        src = os.listdir(os.path.join(cur_path(), 'test_data'))
        dest = self.sp_obj.build_levels(level='var', make_dir=True)

        for file in src:
            shutil.copy(os.path.join(cur_path(), 'test_data', file), dest)

        result = self.sp_obj.search_files('var', pattern='SSM')

        assert should == result


    def test_search_files_ts(self):
        '''
        Testing the file search yielding a pandas DataFrame().
        '''

        files = ['M20161218_051642--_SSM------_S1BIWGRDH1VVD_095_C1003_EU500M_E048N012T6.tif']
        times = extract_times(files, date_position=1, date_format='%Y%m%d_%H%M%S')
        should = pd.DataFrame({'Files': files}, index=times)

        src = os.listdir(os.path.join(cur_path(), 'test_data'))
        dest = self.sp_obj.build_levels(level='var', make_dir=True)

        for file in src:
            shutil.copy(os.path.join(cur_path(), 'test_data', file), dest)

        result = self.sp_obj.search_files_ts('var', pattern='SSM',
                                             starttime='20161218_000000',
                                             endtime='20161224_000000')

        assert all(should == result)


class TestSmartTree(unittest.TestCase):
    '''
    Preliminary tests for SmartTree().
    '''

    def setUp(self):
        self.path = os.path.join(cur_path(), 'test_temp_dir')

    def tearDown(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)


    def test_everything(self):

        hierarchy = ['root', 'sensor', 'mode', 'group',
                     'datalog', 'product', 'wflow', 'grid',
                     'tile', 'var', 'qlook']

        st = SmartTree(self.path,
                       hierarchy, make_dir=True)

        sp = get_test_sp_4_smarttree(sensor='Sentinel-1_CSAR',
                         mode='IWGRDH', group='products',
                         datalog='datasets', product='ssm',
                         wflow='C1003', grid='EQUI7_EU500M',
                         tile='E048N012T6', var='ssm')

        st.add_smartpath(sp)

        sp5 = get_test_sp_4_smarttree(sensor='Sentinel-1_CSAR',
                         mode='IWGRDH', group='products',
                         datalog='datasets', product='ssm',
                         wflow='C1003', grid='EQUI7_EU500M',
                         tile='E054N018T6', var='ssm')

        st.add_smartpath(sp5, make_dir=True)

        sp2 = get_test_sp_4_smarttree(sensor='Sentinel-1_CSAR',
                         mode='IWGRDH', group='products',
                         datalog='datasets', product='ssm',
                         wflow='C1077', grid='EQUI7_EU500M',
                         tile='E048N012T6', var='ssm')

        st.add_smartpath(sp2)

        sp3 = get_test_sp_4_smarttree(sensor='Sentinel-1_CSAR',
                         mode='IWGRDH', group='products',
                         datalog='logfiles')

        st.add_smartpath(sp3)

        sp4 = get_test_sp_4_smarttree(sensor='Sentinel-1_CSAR',
                         mode='IWGRDH', group='products',
                         datalog='datasets', product='resampled',
                         wflow='A0202', grid='EQUI7_EU500M',
                         tile='E048N012T6', var='sig0')

        st.add_smartpath(sp4)

        st.collect_level('datalog')

        st.collect_level('wflow', pattern='C1003')

        a = st['C1003', 'E048N012T6']
        b = st['']


        should = ['M20161218_051642--_SSM------_S1BIWGRDH1VVD_095_C1003_EU500M_E048N012T6.tif',
                  'M20170405_171401--_SSX------_S1AIWGRDH1VVA_015_C1003_EU500M_E048N012T6.tif',
                  'M20170406_050911--_SSM------_S1AIWGRDH1VVD_022_C1003_EU500M_E048N012T6.tif']

        src = os.listdir(os.path.join(cur_path(), 'test_data'))
        dest = sp.build_levels(level='var', make_dir=True)

        for file in src:
            shutil.copy(os.path.join(cur_path(), 'test_data', file), dest)

        result = st['C1003', 'E048N012T6'].search_files('var')

        assert should == result

if __name__ == "__main__":
    unittest.main()
