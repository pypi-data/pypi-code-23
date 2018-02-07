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
Heritage SGRT (experimental) classes.
"""

import os

from geopathfinder.sgrt_naming import full_sgrt_tree



class SgrtFolderName_old_interface():

    """
    Heritage-class from SGRT. This class handles sgrt data (folders)
    structure, using the geopathfinder package.
    """

    def __init__(self, product_id, wflow_id, dir_root,
                 dir_work=None, **kwargs):
        """
        Initializes sgrt data structure.

        Parameters
        ----------
        product_id : str
            Input satellite product ID. The full satalite product id has
            13 characters (e.g. S1AIWGRDH1HHD) at least 3 characters are
            required to identify the satellite (top level in folder structure)
        wflow_id : str
            A 5 digits string starting with a letter (A, B, C, or N)
            e.g. A0110 standing for wflow_name=A01, wflow_version=10
        dir_root : str
            The top level directory sgrt output folder structure will be
            created in that directory
        dir_work : str, optional
            Working directory (default: None).
        """

        self.all_levels = full_sgrt_tree(
            dir_root=dir_root, product_id=product_id, wflow_id=wflow_id,
            **kwargs)

        self.level_1 = self.all_levels.build_levels(level='product')
        self.level_2 = self.all_levels.build_levels(level='group')

        self.dir_root = dir_root
        self.dir_anc = os.path.join(self.level_1, "ancillary")
        self.dir_doc = os.path.join(self.level_1, "documentation")
        self.dir_log = os.path.join(self.level_2, "logfiles")
        if dir_work is not None:
            self.dir_work = os.path.join(dir_work, ".SGRT")
        else:
            self.dir_work = os.path.join(dir_root, ".SGRT")

        self.product_id = product_id.upper()
        self.wflow_id = wflow_id.upper()

        self.build_subdirs(**kwargs)

    def build_subdirs(self, ptop_name=None, grid='EQUI7', ftile=None,
                      sgrt_var_name=None, makedir=False):
        """
        This function builds/updates directories according to the given
        parameters as keywords

        ptop_name : str, optional
            Product top directory (folder) name, in which the wflow
            outputs are stored The ptop_name name are actually coming from
            the workflow configuration files (e.g. ['geocoded', 'resampled']
            from A01_config.xml) NOTE: in the new version onyl ONE ptop_name
            will will be stored. In case of a list of ptop directrories,
            the code should be run in a loop
        grid : str, optional
            Grid reference for the data (default: 'EQUI7').
        ftile : str
            Full tile identifier e.g. 'EU010M_E052N016T1'
        sgrt_var_name : str
            The sgrt variable name is used to create the product
            sub directory name, in which the final product is stored
            NOTE: the ftile keyword should be already provided in order to
            create the product sub directory e.g. SIG0, PLIA, TMENPLIA, ..
        makedir (optional, default is false): flag
            a Flag for making sgrt directory
        NOTE: grid, ftile, and psub_dir (sgrt_var_name) directories will be
             created only if their parent directories are provided.
        NOTE: grid and ftile directories will be created if pir_sub
             sgrt_var_name) is also provided.
        """
        # check optional keywords to continue the directoy path to
        # level_3: product top directory
        # level_4: grid and tile name
        # level_5: product sub directory

        if ptop_name is None:
            raise ValueError(
                "You're using an outdated SGRT folder naming convention!")

        if ftile not in [None, '']:
            if len(ftile) != 17:
                raise ValueError(
                    "According to SGRT Naming Convention the full tile "
                    "name should have 17 characters!")

        if sgrt_var_name not in [None, '']:
            if len(sgrt_var_name) > 9:
                raise ValueError("According to SGRT Naming Convention the"
                                 "sgrt varible name should be not more"
                                 "than 9 characters!")

        levels = sgrt_tree(dir_root=self.level_2, ptop_name=ptop_name,
                           grid='EQUI7', ftile=ftile, wflow_id=self.wflow_id,
                           sgrt_var_name=sgrt_var_name, section='bottom')

        self.level_3 = levels.build_levels(level='wflow')
        self.level_4 = levels.build_levels(level='tile')
        self.level_5 = levels.build_levels(level='var')

        self.ptop_name = ptop_name
        self.dir_ptop = self.level_3
        self.dir_ftile = self.level_4
        self.dir_psub = self.level_5
        self.dir_qlook = levels.build_levels(level='qlook')

        if makedir:
            self.makedirs()

    def makedirs(self):
        """
        Make the directories that start with "dir"
        """
        for k, v in zip(self.__dict__.keys(), self.__dict__.values()):
            if k[0:3] == 'dir':
                makedirs(v)
            else:
                continue


class SGRTFolderName():

    """
    Heritage-class from SGRT. This class handles sgrt data (folders)
    structure, using the geopathfinder package.
    """

    def __init__(self, product_id, wflow_id, dir_root, dir_work=None,
                 **kwargs):
        """
        Initializes sgrt data structure.

        Parameters
        ----------
        product_id : str
            Input satellite product ID. The full satalite product id has
            13 characters (e.g. S1AIWGRDH1HHD) at least 3 characters are
            required to identify the satellite (top level in
            folder structure)
        wflow_id : str
            Work flow ID. A 5 digits string starting with a
            letter (A, B, C, or N) e.g. A0110 standing for wflow_name=A01,
            wflow_version=10.
        dir_root :
            The top level directory. Sgrt output folder structure will be
            created in that directory.
        dir_work : str, optional
            Working directory.
        """
        # function for the sensor and prodcut folders
        if product_id[0:2].lower() == 's1':
            sensor = "Sentinel-1_CSAR"
            product = product_id[3:9].upper()
        elif product_id[0:3].lower() == 'asa':
            sensor = "Envisat_ASAR"
            product = product_id[3:5].upper()
        elif product_id[0:3].lower() == 'asc':
            sensor = 'METOP_ASCAT'
            product = product_id[3:9].upper()
        elif product_id[0:3].lower() == 'sss':
            sensor = 'SCATSAR'
            product = product_id[3:8].upper()
        else:
            raise ValueError('product_id is unknown!')

        # function for the wflow_folder_names
        wflow_folder_names = {
            "A": "preprocessed", "B": "parameters", "C": "products",
            "N": "nrt"}

        wflow_group = wflow_folder_names[wflow_id[0].upper()]

        # function for datasets or logfiles
        datalog = 'datasets'

        # function for the ptop_name
        top_folder = ptop_name

        # function for wflow_id
        wflow = wflow_id

        # function for grid_folder, tile_folder
        grid_folder, tile_folder = "_".join(
            [grid.upper(), ftile.split('_')[0]]), ftile.split('_')[1]

        # function for the sgrt_var_name
        var_folder = sgrt_var_name.lower().rstrip('-')

        # function for qlooks
        qlook = 'qlooks'



def test_folders():
    root_path = r'R:\Projects_work\SAR_NRT_Code_Sprint\Testdata'

    ftf = full_sgrt_tree(
        root_path, sensor='Sentinel-1_CSAR', mode='IWGRDH', group='products', datalog='datasets',
        product='ssm', wflow='C1003', grid='EQUI7_EU500M', tile='E048N012T6', var='ssm',
        make_dir=True)

    print(ftf['grid'])
    print(ftf.search_files('var', pattern=".*SSM.*VV.*", full_paths=True))
    files = ftf.search_files('var', pattern=".*SSM")

    df = ftf.search_files_ts('var', pattern=".*SSM", starttime='20161218_000000', endtime='20161224_000000',
                             full_paths=True)

    print(ftf.search_files('var', pattern='M*', full_paths=True))



if __name__ == '__main__':
    test_folders()
