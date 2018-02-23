"""
setup5_ENSG_Canonical_AA_FASTA_GRCh37.py
This takes the ENSG CDS file, UniProtKb canonical AA file, and ENSG UniProtKb mapping file
1. translate CDS
2. map ENSG to UniProtKb ID
3. match translated CDS to UniProtKB canonical AA
"""

from collections import defaultdict
from csv import reader
from Bio import SeqIO
from os import path
from time import strftime
from ast import literal_eval

codontable = {
    'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
    'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
    'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',
    'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
    'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
    'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
    'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
    'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
    'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
    'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
    'TAC': 'Y', 'TAT': 'Y', 'TAA': '_', 'TAG': '_',
    'TGC': 'C', 'TGT': 'C', 'TGA': '_', 'TGG': 'W',
}
codon_list = list(codontable.keys())
stop_codon_list = ["TAA", "TAG", "TGA"]
def translate_dna(sequence):
    protein_sequence = ""
    for n in range(0, len(sequence), 3):
        if sequence[n:n + 3] in stop_codon_list:
            break
        else:
            if len(sequence[n:n + 3]) == 3 and sequence[n:n + 3] in codon_list:
                protein_sequence += codontable[sequence[n:n + 3]]
    return protein_sequence

def does_file_exist(file_location, make = True):
    try:
        open(file_location,"r")
    except FileNotFoundError:
        if make:
            open(file_location, "w")
        return False
    return True

today = strftime("%Y%m%d")

file_folder = path.dirname(path.abspath(__file__)).replace("/scripts/setup", "")
setup_folder = file_folder + "/reference_data/setup"
data_folder = file_folder + "/reference_data/data_to_run_main"

# ENSG CDS FASTA from setup2
ENSG_CDS_file = setup_folder + "/ENSG_CDS_GRCh37.fa"

# Make UniProtKb ID to canonical AA sequence dictionary from setup3
UniProtKb_to_Canonical_AA_dict = defaultdict(str)
UniProtKb_to_Canonical_AA_file = setup_folder + "/UniProtKb_ID_Canonical_AA.fa"
with open(UniProtKb_to_Canonical_AA_file, "r") as file:
    parsed_file = SeqIO.parse(file, "fasta")
    for rec in parsed_file:
        UniProtKb_to_Canonical_AA_dict[str(rec.id)] = str(rec.seq)

# Make ENSG to UniProtKb ID dictionary from setup4
ENSG_to_UniProtKb_dict = defaultdict(list)
ENSG_to_UniProtKb_file = data_folder + "/ENSG_to_UniProtKb_GRCh37.txt"
with open(ENSG_to_UniProtKb_file, "r") as file:
    file_csv = reader(file, delimiter = "\t")
    for line in file_csv:
        ENSG = line[0]
        UniProtKb = line[1]
        ENSG_to_UniProtKb_dict[ENSG] = literal_eval(UniProtKb)

# Outputs
ENSG_to_Canonical_AA_output = data_folder + "/ENSG_to_Canonical_AA_GRCh37.fa"
ENSG_to_Canonical_AA_CDS_output = data_folder +"/ENSG_to_Canonical_AA_CDS_GRCh37.fa"

# Match ENSG to canonical amino acid sequence
if not does_file_exist(ENSG_to_Canonical_AA_output, make = False) or not does_file_exist(ENSG_to_Canonical_AA_CDS_output, make = False):
    print("There will be fewer genes matched to canonical sequence than total "
          "genes because there are transcript variants that do not match the "
          "canonical sequence.\n")
    count = 0
    count_matched = 0
    with open(ENSG_CDS_file, "r") as file,\
        open(ENSG_to_Canonical_AA_output, "w") as output1,\
        open(ENSG_to_Canonical_AA_CDS_output, "w") as output2:
        file_parsed = SeqIO.parse(file, "fasta")
        for rec in file_parsed:
            # Reset matched to False for each new ENSG
            matched = False
            count += 1
            ENSG = str(rec.id).partition(".")[0]
            CDS = str(rec.seq)
            UniProtKb_list = ENSG_to_UniProtKb_dict[ENSG]
            # Skip ENSGs not mapped UniProtKb IDs
            if UniProtKb_list == []:
                continue
            # Translate ENSG CDS
            AA_seq = translate_dna(CDS)
            # Extract canonical amino acid sequences for all UniProtKb IDs mapped to ENSG
            # Prints run updates every 1000 ENSGs analyzed
            if count % 1000 == 0:
                print(str(count) + " ENSGs analyzed, " + str(count_matched) + " matched to canonical AA sequence.")
            for UniProtKb in UniProtKb_list:
                if UniProtKb == "":
                    continue
                # Already found matching canonical amino acid sequence for this ENSG, stop looking at other mapped UniProtKb IDs
                if matched:
                    continue
                Canonical_AA = UniProtKb_to_Canonical_AA_dict[UniProtKb]
                # Output matched translated ENSG CDS to mapped UniProtKb canonical AA sequence
                if AA_seq == Canonical_AA:
                    output1.write(">" + str(ENSG) + "_" + str(UniProtKb) + "\n" + str(Canonical_AA) + "\n")
                    output2.write(">" + str(ENSG) + "_" + str(UniProtKb) + "\n" + str(CDS) + "\n")
                    count_matched += 1
                    matched = True
    print("\n")

