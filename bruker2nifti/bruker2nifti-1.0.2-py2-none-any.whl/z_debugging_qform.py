from bruker2nifti.z_scan_converter import convert_a_scan

from bruker2nifti.z_study_converter import convert_a_study

from bruker2nifti.converter import Bruker2Nifti

# pfo_scan = '/Users/sebastiano/Desktop/test_data/1305/1'
# pfo_output = '/Users/sebastiano/Desktop/test_data/three'
#
# convert_a_scan(pfo_input_scan=pfo_scan, pfo_output=pfo_output)
#
# pfo_study = '/Users/sebastiano/Desktop/test_data/1305'
# pfo_output = '/Users/sebastiano/Desktop/test_data/'
#
# convert_a_study(pfo_study, pfo_output, study_name='1305_', correct_slope=True)
#

bru = Bruker2Nifti('/Users/sebastiano/Desktop/3103', '/Users/sebastiano/Desktop/output_test/')
