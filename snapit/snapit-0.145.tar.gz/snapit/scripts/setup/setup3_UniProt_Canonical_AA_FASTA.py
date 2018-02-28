"""
setup3_UniProt_Canonical_AA_FASTA.py
This takes the canonical AA sequence file from UniProtKb
1. convert to FASTA file with UniProtKb ID identifier and canonical AA sequences
"""

from requests import get
from Bio import SeqIO
from os import path

def does_file_exist(file_location, make = True):
    try:
        open(file_location,"r")
    except FileNotFoundError:
        if make:
            open(file_location, "w")
        return False
    return True

file_folder = path.dirname(path.abspath(__file__)).replace("/scripts/setup", "")
initial_folder = file_folder + "/reference_data/initial_download"
output_folder = file_folder + "/reference_data/setup"

input_file = initial_folder + "/UniProtKb_Metadata_Canonical_AA.fa"
output_file = output_folder + "/UniProtKb_ID_Canonical_AA.fa"
canonical_sequence_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=organism:%22Homo%20sapiens%20[9606]%22&fil=&format=fasta&force=yes"

# Download canonical amino acid sequences from UniProtKb
if not does_file_exist(input_file, make = False):
    canonical_sequence = get(canonical_sequence_link).text
    with open(input_file, "w") as f:
        f.write(canonical_sequence)

# Convert downloaded file to FASTA format
if not does_file_exist(output_file, make = False):
    with open(input_file, "r") as file,\
        open(output_file, "w") as output:
        for rec in SeqIO.parse(file, "fasta"):

            # Extract UniProtKb ID
            UniProtKb = rec.id.partition("|")[2].partition("|")[0]
            # Extract canonical amino acid sequence
            sequence = str(rec.seq)

            # Write output in FASTA format
            output.write(">" + UniProtKb + "\n" + sequence + "\n")