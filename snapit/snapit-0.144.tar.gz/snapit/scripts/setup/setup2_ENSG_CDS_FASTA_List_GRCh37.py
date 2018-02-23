"""
setup2_ENSG_CDS_FASTA_List_GRCh37.py
This takes the CDS annotation file from Ensembl
1. convert to FASTA file with ENSG identifier and CDS sequences
2. list all ENSGs
"""

from Bio import SeqIO
from os import path

def does_file_exist(file_location, make = True):
    try:
        open(file_location, "r")
        return True
    except FileNotFoundError:
        if make == True:
            open(file_location, "w")
        return False

file_folder = path.dirname(path.abspath(__file__)).replace("/scripts/setup", "")
download_folder = file_folder + "/reference_data/initial_download"
output_folder = file_folder + "/reference_data/setup"

fasta_file = download_folder + "/Homo_sapiens.GRCh37.cds.all.fa"
file_parsed = SeqIO.parse(open(fasta_file, "r"), "fasta")
output_ENSG_fasta = output_folder + "/ENSG_CDS_GRCh37.fa"
output_ENSG_list = output_folder + "/ENSG_List_GRCh37.txt"

# Output FASTA
if not does_file_exist(output_ENSG_fasta, make = False) or not does_file_exist(output_ENSG_fasta, make = False):
    # Unique list of ENSGs
    ENSG_list = []
    with open(output_ENSG_fasta, "w") as output_fasta,\
        open(output_ENSG_list, "w") as output_list:
        for parsed_line in file_parsed:

            # Extract ENSG
            description = parsed_line.description
            ENSG = description.partition("gene:")[2].partition(" gene_biotype")[0]
            ENSG = ENSG.partition(".")[0]
            # Extract CDS sequence
            sequence = parsed_line.seq

            # Write output in FASTA format
            output_fasta.write(">" + ENSG + "\n" + str(sequence) + "\n")

            # Write unique ENSGs to output
            if ENSG not in ENSG_list:
                ENSG_list.append(ENSG)
                output_list.write(ENSG + "\n")
