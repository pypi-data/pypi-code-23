"""
setup4_ENSG_UniProtKb_GRCh38.py
This takes the list of all ENSGs from Ensembl
1. map to corresponding UniProtKb ID
"""

from csv import reader
import csv
import sys
from collections import defaultdict
from os import path
csv.field_size_limit(sys.maxsize)

def does_file_exist(file_location, make = True):
    try:
        open(file_location,"r")
    except FileNotFoundError:
        if make:
            open(file_location, "w")
        return False
    return True

file_folder = path.dirname(path.abspath(__file__)).replace("/scripts/setup", "")
setup_folder = file_folder + "/reference_data/setup"
initial_folder = file_folder + "/reference_data/initial_download"
data_folder = file_folder + "/reference_data/data_to_run_main"

ID_mapping = initial_folder + "/HUMAN_9606_idmapping_selected.txt"
all_ENSG_list = setup_folder + "/ENSG_List_GRCh38.txt"
ENSG_to_UniProtKb = data_folder + "/ENSG_to_UniProtKb_GRCh38.txt"

if not does_file_exist(ENSG_to_UniProtKb, make = False):
    ENSG_list = []
    map_dictionary = defaultdict(list)
    with open(ID_mapping, "r") as map_file,\
        open(all_ENSG_list, "r") as ENSG_file,\
        open(ENSG_to_UniProtKb, "w") as output:
        ENSG_file_csv = reader(ENSG_file, delimiter = "\t")
        map_file_csv = reader(map_file, delimiter = "\t")

        for line in ENSG_file_csv:
            ENSG = line[0]
            ENSG_list.append(ENSG)

        for line in map_file_csv:
            # Extract UniProtKb ID
            UniProtKb = str(line[0])

            # Extract ENSG
            identities_list = line[1:]
            ENSG_from_map = [x for x in line if x.startswith("ENSG")]
            ENSG_from_map = str(ENSG_from_map).strip("'[]").split("; ")

            # Add matches to dictionary
            if ENSG_from_map != ['']:
                for e in ENSG_from_map:
                    map_dictionary[e].append(UniProtKb)

        # Write output from dictionary
        for ENSG in ENSG_list:
            output.write(str(ENSG) + "\t" + str(map_dictionary[ENSG]) + "\n")
