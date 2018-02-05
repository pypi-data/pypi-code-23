"""
setup.py
This runs the entire setup for the extracellular analysis.
"""

import sys
from os import path

def check_empty_file(file_location):
    if path.getsize(file_location) > 0:
        return False
    else:
        return True

file_folder = path.dirname(path.abspath(__file__))
sys.path.insert(0, file_folder + "/scripts/setup/")

genome = int(input("\nWhich reference genome would you like to setup? (1-3):\n"
                   "1\tGRCh37/hg19\n"
                   "2\tGRCh38/hg38\n"
                   "3\tAll genomes\n") or 3)

if True:
#try:
    # Downloads all initial files
    print("\nThis will take some time.\n")
    # Takes CDS file from Ensembl and converts it to FASTA format with ENSG as the heading
    print("Running setup1_Download_Files")
    if genome == 1 or 3:
        import setup1_Download_Files_GRCh37
    if genome == 2 or 3:
        import setup1_Download_Files_GRCh38

    # Takes CDS file from Ensembl and converts it to FASTA format with ENSG as the heading
    print("Running setup2_ENSG_CDS_FASTA_List_GRCh38\n")
    if genome == 1 or 3:
        import setup2_ENSG_CDS_FASTA_List_GRCh37
    if genome == 2 or 3:
        import setup2_ENSG_CDS_FASTA_List_GRCh38

    # Gets canonical AA sequence from UniProt
    print("Running setup3_UniProt_Canonical_AA_FASTA\n")
    import setup3_UniProt_Canonical_AA_FASTA

    # Translate ENSG to UniProt ID
    print("Running setup4_ENSG_UniProtKb\n")
    if genome == 1 or 3:
        import setup4_ENSG_UniProtKb_GRCh37
    if genome == 2 or 3:
        import setup4_ENSG_UniProtKb_GRCh38

    # Match all ENSG CDS to its canonical AA sequence. This throws out all ENSG that don't match with the canonical sequence
    print("Running setup5_ENSG_Canonical_AA_FASTA\n")
    if genome == 1 or 3:
        import setup5_ENSG_Canonical_AA_FASTA_GRCh37
    if genome == 2 or 3:
        import setup5_ENSG_Canonical_AA_FASTA_GRCh38

    # Creates input for TMHMM manual analysis
    print("Running setup6_Make_TMHMM_Input_from_ENSG_Canonical_AA\n")
    if genome == 1 or 3:
        import setup6_Make_TMHMM_Input_from_ENSG_Canonical_AA_GRCh37
    if genome == 2 or 3:
        import setup6_Make_TMHMM_Input_from_ENSG_Canonical_AA_GRCh38
#except:
#    exit("Setup was not run. Something went wrong during this step.")
