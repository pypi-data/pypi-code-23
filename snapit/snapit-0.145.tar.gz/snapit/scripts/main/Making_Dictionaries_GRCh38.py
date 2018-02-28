"""
Making_Dictionaries_Extracellular_GRCh38.py
"""


from collections import defaultdict
from Bio import SeqIO
from csv import reader
from re import finditer
from os import path
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
stop_codon_list = ["TAA","TGA","TAG"]

def translate_dna(sequence, start = 0, readthrough = False):
    protein_sequence = ""
    for n in range(0, len(sequence), 3):
        if sequence[n + start:n + 3 + start] in stop_codon_list and not readthrough:
            break
        else:
            if len(sequence[n + start:n + 3 + start]) == 3 and sequence[n + start:n + 3 + start] in codon_list:
                protein_sequence += codontable[sequence[n + start:n + 3 + start]]
    return protein_sequence


file_folder = path.dirname(path.abspath(__file__))
main_folder = file_folder.replace("/scripts/main", "")
setup_folder = main_folder + "/reference_data/setup"
download_folder = main_folder + "/reference_data/initial_download"
data_folder = main_folder + "/reference_data/data_to_run_main"

# ENSG to UniProtKb dictionary
ENSG_to_UniProtKb_dict = defaultdict(list)
ENSG_to_UniProtKb_file = data_folder + "/ENSG_to_UniProtKb_GRCh38.txt"
with open(ENSG_to_UniProtKb_file, "r") as file:
    file_csv = reader(file, delimiter = "\t")
    for line in file_csv:
        ENSG = line[0]
        UniProtKb = line[1]
        ENSG_to_UniProtKb_dict[ENSG] = literal_eval(UniProtKb)


# ENSG to TMHMM transmembrane annotations dictionary
ENSG_to_TMHMM_dict = defaultdict(list)
ENSG_to_TMHMM_file = data_folder + "/TMHMM_TM_Only_GRCh38.txt"
genes_with_TMHMM_domain_list = []
with open(ENSG_to_TMHMM_file, "r") as file:
    file_csv = reader(file, delimiter = "\t")
    for line in file_csv:
        topology_o_i = ""
        TMHMM_extracellular_domain = []
        TMHMM_intracellular_domain = []
        ENSG = line[0]
        genes_with_TMHMM_domain_list.append(ENSG)
        length = int(line[1].partition("len=")[2])
        topology_raw = line[5]
        topology = topology_raw.partition("Topology=")[2]
        TMHMM_transmembrane_domain = [m.group() for m in finditer("\d+(-)\d+", topology)]
        inside_outside_index = [m.start() for m in finditer("[oi]", topology)]
        for index in inside_outside_index:
            topology_o_i += topology[index]
        cyto_extra_domains = []
        for a, domain_range in enumerate(TMHMM_transmembrane_domain):
            start = int(domain_range.partition("-")[0])
            if a == 0:
                cyto_extra_domains.append("1-" + str(start - 1))
            else:
                cyto_extra_domains.append(str(end + 1) + "-" + str(start - 1))
            if a == len(TMHMM_transmembrane_domain) - 1:
                end = int(domain_range.partition("-")[2])
                cyto_extra_domains.append(str(end + 1) + "-" + str(length))
            end = int(domain_range.partition("-")[2])
        for a, domain_range in enumerate(cyto_extra_domains):
            out_or_in = topology_o_i[a]
            if out_or_in == "o":
                TMHMM_extracellular_domain.append(domain_range)
            elif out_or_in == "i":
                TMHMM_intracellular_domain.append(domain_range)
        if [TMHMM_intracellular_domain, TMHMM_transmembrane_domain, TMHMM_extracellular_domain] != ENSG_to_TMHMM_dict[ENSG]:
            ENSG_to_TMHMM_dict[ENSG].extend((TMHMM_intracellular_domain, TMHMM_transmembrane_domain, TMHMM_extracellular_domain))


# ENSG to canonical amino acid sequence dictionary
ENSG_to_Canonical_AA_dict = defaultdict(str)
ENSG_to_Canonical_AA_file = data_folder + "/ENSG_to_Canonical_AA_GRCh38.fa"
with open(ENSG_to_Canonical_AA_file, "r") as file:
    file_parsed = SeqIO.parse(file, "fasta")
    for rec in file_parsed:
        ENSG = rec.id
        Canonical_AA = str(rec.seq)
        ENSG_to_Canonical_AA_dict[ENSG] = Canonical_AA


# ENSG to CDS dictionary
ENSG_to_Canonical_AA_CDS_dict = defaultdict(str)
ENSG_to_Canonical_AA_CDS_file = data_folder + "/ENSG_to_Canonical_AA_CDS_GRCh38.fa"
with open(ENSG_to_Canonical_AA_CDS_file, "r") as file:
    file_parsed = SeqIO.parse(file, "fasta")
    for rec in file_parsed:
        ENSG = rec.id
        CDS = str(rec.seq)
        if CDS not in ENSG_to_Canonical_AA_CDS_dict[ENSG]:
            if ENSG_to_Canonical_AA_CDS_dict[ENSG] != [] and "N" in CDS:
                continue
            else:
                ENSG_to_Canonical_AA_CDS_dict[ENSG] = CDS


# Chromosome number to chromosome sequence dictionary
Chromosome_to_Sequence_dict = defaultdict(str)
human_genome_file = data_folder + "/hg38.fa"
human_genome = SeqIO.parse(human_genome_file, "fasta")
for rec in human_genome:
    chromosome_read = rec.seq
    chr = rec.id
    Chromosome_to_Sequence_dict[chr] = chromosome_read


# Gene to description dictionary
Gene_Description_dict = defaultdict(str)
gene_description_file = data_folder + "/Gene_Description.txt"
with open(gene_description_file, "r") as file:
    file_csv = reader(file, delimiter ="\t")
    for line in file_csv:
        ENSG = line[0]
        description = line[2]
        Gene_Description_dict[ENSG] = description

