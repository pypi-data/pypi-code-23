from subprocess import check_output
import os


# # Describe the version relative to last tag
# command_git = ['git', 'describe', '--match', 'v[0-9]*']
# version_buf = check_output(command_git).rstrip()
#
# print(version_buf)
#
# # Exclude the 'v' for PEP440 conformity, see
# # https://www.python.org/dev/peps/pep-0440/#public-version-identifiers
# version_buf = version_buf[1:]
#
# print(version_buf)

import os

from bruker2nifti.converter import Bruker2Nifti

if __name__ == '__main__':
    root_dir = '/path/to/bruker2nifti/repo'
    pfo_study_in = os.path.join('/Users/sebastiano/Desktop/3103')
    pfo_study_out = '/Users/sebastiano/Desktop/test_converter/'

    print(os.path.isdir(pfo_study_out))

    # instantiate a converter
    bru = Bruker2Nifti(pfo_study_in, pfo_study_out, study_name='my_study')
    # select the options (attributes) you may want to change - the one shown below are the default one:
    bru.verbose = 2
    bru.correct_slope = True
    bru.get_acqp = False
    bru.get_method = False
    bru.get_reco = False
    bru.nifti_version = 1
    bru.qform_code = 1
    bru.sform_code = 2
    bru.save_human_readable = True
    bru.save_b0_if_dwi = True
    # Check that the list of scans and the scans names automatically selected makes some sense:
    print(bru.scans_list)
    print(bru.list_new_name_each_scan)
    # call the function convert, to convert the study:
    bru.convert()

