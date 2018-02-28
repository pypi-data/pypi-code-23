"""
setup6_Make_TMHMM_Input_from_ENSG_Canonical_AA_GRCh37.py
This takes matched ENSG canonical AA sequences
1. submit to TMHMM for transmembrane and topological annotation
This script uses automated TMHMM from installed API
1. must install stand-alone package first
2. may be run manually on TMHMM webserver
"""

from csv import reader
from os import path
import subprocess

def does_file_exist(file_location, make = True):
    try:
        open(file_location,"r")
        return True
    except FileNotFoundError:
        if make:
            open(file_location, "w")
        return False

file_folder = path.dirname(path.abspath(__file__)).replace("/scripts/setup", "")
setup_folder = file_folder + "/reference_data/setup"
data_folder = file_folder + "/reference_data/data_to_run_main"

input_file = data_folder + "/ENSG_to_Canonical_AA_GRCh37.fa"
TMHMM_output = setup_folder + "/TMHMM_Result_GRCh37.txt"
output_file = data_folder + "/TMHMM_TM_Only_GRCh37.txt"

if not does_file_exist(output_file, make = False):
    # Submit job to TMHMM Server v. 2.0
    # Requires TMHMM API to be installed
    print("Submitting job to TMHMM 2.0...")
    TMHMM_command = file_folder + "/Install/tmhmm-2.0c/bin/tmhmm "
    subprocess.call(TMHMM_command + input_file + " > " + TMHMM_output, shell = True)

    # Filter to select for only transmembrane data
    print("Filtering for only transmembrane annotation...\n")
    with open(TMHMM_output, "r") as file,\
        open(output_file, "w") as output:
        file_csv = reader(file, delimiter='\t')
        for line in file_csv:
            helices = int(line[4].partition("PredHel=")[2])
            # Must have at least 1 helix to be transmembrane
            if helices == 0:
                continue
            else:
                line_to_write = "\t".join(line)
                output.write(line_to_write + "\n")
