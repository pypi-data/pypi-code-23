"""
multiple-comparison.py
This takes a formatted input rMATS file and identifies extracellular cassette exons.
multiple-comparison denotes the data comes from the multiple datasets, where only PSI is included in the input.
"""

# Import modules
from csv import DictReader
from collections import defaultdict
from os import path, makedirs, remove
import glob
import sys
import pandas as pd
import difflib
import io
from Bio.Blast import NCBIXML
from multiprocessing import Pool
import subprocess

# Define functions
codon_table = {
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
codon_list = list(codon_table.keys())
stop_codon_list = ["TAA", "TGA", "TAG"]

# Translate DNA sequence to AA sequence
def translate_dna(sequence, readthrough = False, start = 0):
    protein_sequence = ""
    for n in range(0, len(sequence), 3):
        # Stop reading at stop codon
        if sequence[(n + start):(n + start + 3)] in stop_codon_list and not readthrough:
            break
        # Continue reading until encounter stop codon if readthrough == False
        else:
            if len(sequence[n + start:n + 3 + start]) == 3 and sequence[n + start:n + 3 + start] in codon_list:
                protein_sequence += codon_table[sequence[n + start:n + 3 + start]]
    return protein_sequence

# Reverse complement DNA sequence for '-' strand
def reverse_complement(seq):
    seq = seq.upper()
    # Complementary base pairs
    seq_dict = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    return "".join([seq_dict[base] for base in reversed(seq)])


# Check if files exist
def does_file_exist(file_location, make = True):
    try:
        open(file_location, "r")
    # File does not exist
    except FileNotFoundError:
        # Write file
        if make:
            open(file_location, "w")

# Convert a list of sequences into fasta format
def makeFasta(sequences):
    output = ""
    # x = index, y = sequence
    for x, y in enumerate(sequences):
        # > index
        # sequence
        output = output + '>' + str(x) + '\n' + str(y) + '\n'
    return output

# Protein BLAST a list of sequences against RefSeq human protein database
def BLASTp(query, index):
    if query:
        isoforms = []
        # Write temp fasta file
        seqFile = tempFolder + "seq_" + str(index) + ".fasta"
        with open(seqFile, "w") as seq1:
            seq1.write(makeFasta(query))
        # Run BLAST in command line
        # Directory hard coded, need to change!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # BLAST against RefSeq human protein database
        # Set BLASTDB environmental variable
        # Convert byte to string
        output = subprocess.check_output(
            file_folder + "/Install/ncbi-blast-2.7.1+/bin/blastp -query " + seqFile + " -db human.all.protein.faa -outfmt 5 -num_threads 4",
            env={'BLASTDB': file_folder + '/Install/ncbi-blast-2.7.1+/blastdb'}, shell=True).decode(
            "utf-8")
        remove(seqFile)
        # Parse output as XML
        blast_result_record_list = NCBIXML.parse(io.StringIO(output))
        # Print BLAST hit title and expected score
        for blast_result_record in blast_result_record_list:
            for alignment in blast_result_record.alignments:
                for hsp in alignment.hsps:
                    isoforms.append([alignment.title, hsp.expect, hsp.query])
        return isoforms
    else:
        return []

# Map exons to CDS and UTR
def UTR_test_and_find_best_match(exon0Seq, exon2Seq, CDS, matching_aa_seq):
    output_match_list = []
    # Translate CDS
    translatedCDS = translate_dna(CDS)
    # Upstream and downstream exons
    for exon_seq in [exon0Seq, exon2Seq]:
        match_score = 0
        CDS_match_start_index = 0
        CDS_match_end_index = 0
        UTR5 = False
        UTR3 = False
        match_list = [match_score, CDS_match_start_index, CDS_match_end_index, UTR5, UTR3, CDS]
        # Perfect match, exon sequence is in CDS
        if str(exon_seq) in str(CDS):
            # 1 is highest score: 100% match
            match_score = 1
            # Start index of CDS where exon is matched > AA start position of downstream exon > upper bound of cassette exon
            CDS_match_start_index = CDS.find(exon_seq)
            # End index of CDS where exon is matched > AA end position of upstream exon > lower bound of cassette exon
            CDS_match_end_index = CDS_match_start_index + len(exon_seq)
            # Translated CDS maps to canonical AA sequence
            if translatedCDS in matching_aa_seq:
                match_list = [match_score, CDS_match_start_index, CDS_match_end_index, UTR5, UTR3, CDS]
                output_match_list.append(match_list)
        # Not perfect match
        else:
            # CDS is protein coding sequence,excluding 5' UTR and 3' UTR
            # 5' UTR defined as first 15 nucleotides of CDS
            UTR5_seq = CDS[:15]
            # 3' UTR defined as last 15 nucleotides of CDS
            UTR3_seq = CDS[-15:]
            # 5' UTR sequence found in upstream or downstream exon > CDS begins downstream of UTR > cassette exon is in UTR if 5' UTR is in downstream exon
            if UTR5_seq in exon_seq:
                if exon_seq == exon2Seq:
                    UTR5 = True
                # Find exon region without UTR
                match_start_index_of_ex = exon_seq.find(UTR5_seq)
                match_end_index_of_ex = len(exon_seq)
                exon_wo_UTR = exon_seq[match_start_index_of_ex:match_end_index_of_ex]
                match_score = len(exon_wo_UTR) / len(exon_seq)
                # Map exon sequence without UTR to CDS
                CDS_match_start_index = CDS.find(exon_wo_UTR)
                CDS_match_end_index = CDS_match_start_index + len(exon_wo_UTR)
                # Should match beginning but CDS_match_start_index = -1 if exon_wo_UTR not within CDS so we define as not matched
                if CDS_match_start_index != 0:
                    UTR5 = False
                    match_score = 0
            # 3' UTR sequence found in upstream or downstream exon > CDS begins upstream of UTR > cassette exon is in UTR if 3' UTR is in upstream exon
            if UTR3_seq in exon_seq:
                if exon_seq == exon0Seq:
                    UTR3 = True
                # Find exon region without UTR
                match_end_index_of_ex = exon_seq.find(UTR3_seq) + len(UTR3_seq)
                match_start_index_of_ex = 0
                exon_wo_UTR = exon_seq[match_start_index_of_ex:match_end_index_of_ex]
                match_score = len(exon_wo_UTR) / len(exon_seq)
                # Map exon sequence wihtout UTR to CDS
                CDS_match_start_index = CDS.find(exon_wo_UTR)
                CDS_match_end_index = CDS_match_start_index + len(exon_wo_UTR)
                # Should match end but algorithm will occasionally mess up so we define as not matched
                if CDS_match_end_index != len(CDS):
                    UTR3 = False
                    match_score = 0
            # Only if translated CDS matches AA sequence
            if translatedCDS == matching_aa_seq:
                match_list = [match_score, CDS_match_start_index, CDS_match_end_index, UTR5, UTR3, CDS]
                output_match_list.append(match_list)
            # Not perfect match or in UTR, attempt to match exon sequence to CDS
            else:
                match_score = 0.0
                # Find max similarity
                for index_start in range(0, (len(CDS) - len(exon_seq))):
                    candidate = CDS[index_start:index_start + len(exon_seq)]
                    compare = difflib.SequenceMatcher(None, exon_seq, candidate)
                    # similarity = 2 * shared element / total elements in two strings, 1.0 is the highest score
                    similarity = compare.ratio()
                    if similarity > match_score:
                        match_score = similarity
                        CDS_match_start_index = index_start
                        CDS_match_end_index = index_start + len(exon_seq)
                # Only if translated CDS matches AA sequence
                if translatedCDS == matching_aa_seq:
                    match_list = [match_score, CDS_match_start_index, CDS_match_end_index, UTR5, UTR3, CDS]
                    output_match_list.append(match_list)
    return output_match_list

# Localizes cassette exon to extracellular domain of protein
def localizeCassetteExon(upExonEnd, downExonStart, extraDomains, notAligned):
    exonsMatched = "N/A"
    # If protein has annotated extracellular domain
    if extraDomains:
        # Get boundary positions of extracellular domain
        for x in extraDomains:
            lowerBound = x[0]
            upperBound = x[1]
            # If exons aligned to CDS
            if notAligned == "Aligned":
                # Both exons start and end positions fall within extracellular domain
                if lowerBound < int(upExonEnd) < int(downExonStart) < upperBound:
                    exonsMatched = "Both"
            elif notAligned == "Downstream":
                # Upstream exon end positions falls within extracellular domain
                if lowerBound < int(upExonEnd) < upperBound:
                    exonsMatched = "Upstream"
            elif notAligned == "Upstream":
                # Downstream exon start position falls within extracellular domain
                if lowerBound < int(downExonStart) < upperBound:
                    exonsMatched = "Downstream"
    return exonsMatched


# Find possible parent isoforms that display splicing pattern
def findIsoform(seq0, seq1, seq2, strand, index, threshold, junction):
    # Sequences must be able to encode at least 1 codon
    if len(seq0) >= 3 and len(seq1) >= 3 and len(seq2) >= 3:
        try:
            if strand == '+':
                # 3 possible reading frames, cassette included
                readingFrame1 = translate_dna(seq0[len(seq0) - junction:] + seq1 + seq2[:junction])
                readingFrame2 = translate_dna(seq0[len(seq0) - junction + 1:] + seq1 + seq2[:junction])
                readingFrame3 = translate_dna(seq0[len(seq0) - junction + 2:] + seq1 + seq2[:junction])
                # 3 possible reading frames, cassette skipped
                readingFrame4 = translate_dna(seq0[len(seq0) - junction:] + seq2[:junction])
                readingFrame5 = translate_dna(seq0[len(seq0) - junction + 1:] + seq2[:junction])
                readingFrame6 = translate_dna(seq0[len(seq0) - junction + 2:] + seq2[:junction])
            if strand == '-':
                readingFrame1 = translate_dna(seq2[len(seq2) - junction:] + seq1 + seq0[:junction])
                readingFrame2 = translate_dna(seq2[len(seq2) - junction + 1:] + seq1 + seq0[:junction])
                readingFrame3 = translate_dna(seq2[len(seq2) - junction + 2:] + seq1 + seq0[:junction])
                readingFrame4 = translate_dna(seq2[len(seq2) - junction:] + seq0[:junction])
                readingFrame5 = translate_dna(seq2[len(seq2) - junction + 1:] + seq0[:junction])
                readingFrame6 = translate_dna(seq2[len(seq2) - junction + 2:] + seq0[:junction])
            possibleAASeqsInc = [readingFrame1, readingFrame2, readingFrame3]
            possibleAASeqsSkip = [readingFrame4, readingFrame5, readingFrame6]
            # BLAST exon combinations (cassette included) against RefSeq human protein database, keep lowest expected score
            isoform1_list = []
            blast = BLASTp(possibleAASeqsInc, index)
            try:
                eScore = defaultdict(list)
                for x in blast:
                    eScore[x[0], x[2]].append(x[1])
                for k, v in eScore.items():
                    minEScore = min(v)
                    if minEScore < threshold:
                        isoform1_list.append([k, minEScore])
            except:
                pass
            # BLAST exon combinations (cassette excluded) against RefSeq human protein database, keep lowest expected score
            isoform2_list = []
            blast = BLASTp(possibleAASeqsSkip, index)
            try:
                eScore = defaultdict(list)
                for x in blast:
                    eScore[x[0], x[2]].append(x[1])
                for k, v in eScore.items():
                    minEScore = min(v)
                    if minEScore < threshold:
                        isoform2_list.append([k, minEScore])
            except:
                pass
            return [isoform1_list, isoform2_list]
        except:
            return []
    else:
        return []

# Set directory tree to working directory
file_folder = path.dirname(path.abspath(__file__))

# Make temp folder
if not path.exists(file_folder + "/Temp/"):
    makedirs(file_folder + "/Temp/")
tempFolder = file_folder + "/Temp/"

# Make input folder
if not path.exists(file_folder + "/Input_Files/"):
    makedirs(file_folder + "/Input_Files/")
input_file_ready = "N"
while input_file_ready == "N":
    input_files_folder = file_folder + "/Input_Files/"
    input_files_folder_text_only = input_files_folder + "*.txt"
    list_of_raw_files = glob.glob(input_files_folder_text_only)
    if not list_of_raw_files:
        print("You need to put your rMATS output in 'Input_Files' for this to work!")
        input_file_ready = input(
            "Once you've placed an input file in there, type 'Y' and if you would like to close this and work on it later type 'N'\n")
        if input_file_ready == "y" or input_file_ready == "Y":
            continue
        elif input_file_ready == "n" or input_file_ready == "N":
            exit("Please start over once you have files in the Input_Files folder")
    else:
        input_file_ready = "Y"

# Read input file
input_files_folder = file_folder + "/Input_Files/"
input_files_folder_text_only = input_files_folder + "*.txt"
list_of_raw_files = glob.glob(input_files_folder_text_only)
print("Select the Input File for splice isoform analysis:\n(separate each choice with a comma and a space)")
for (input_file_number_raw, text_file_raw) in enumerate(list_of_raw_files):
    text_file_raw = text_file_raw.replace(input_files_folder, "").replace(".txt", "")
    print(str(input_file_number_raw + 1) + "\t" + text_file_raw)

# Ask user to select input file
input_file_File_name_base_number_list = [int(x) - 1 for x in str(input()).split(", ")]

input_file_list = []
for input_file_File_name_base_number in input_file_File_name_base_number_list:
    input_file_name = list_of_raw_files[input_file_File_name_base_number].replace(input_files_folder, "").replace(".txt", "")
    input_file_list.append(input_file_name)

# List chosen input files
input_file_list_to_write = ", ".join(input_file_list)
print("\nYou have selected " + input_file_list_to_write)

# Ask user to input genome build
genome = int(input("\nWhich reference genome was used for this dataset? (1/2):\n"
                   "1\tGRCh38/hg38\n"
                   "2\tGRCh37/hg19\n"))

# Ask user to input percent match threshold for aligning exons to CDS
match_threshold = float(input("\nWhat percent of the exon must align to the CDS to be called a match? (0.0-1.0):\n") or 0.9)

# Import annotations and dictionaries needed for this code
sys.path.insert(0, file_folder + "/scripts/main")

# Updating annotations from UniProt
from Update_Annotations import genes_with_topo_domain_list, missing_topo_domain_gene_list, \
    UniProtKb_to_Topological_Domains_dict, UniProtKb_to_Subcell_Loc_dict, cell_surface_annotation_list

# Making dictionaries that will be needed for this code
print("\nPlease wait while we make dictionaries...")
if genome == 1:
    from Making_Dictionaries_GRCh38 import ENSG_to_TMHMM_dict, ENSG_to_UniProtKb_dict, ENSG_to_Canonical_AA_dict, \
        ENSG_to_Canonical_AA_CDS_dict, genes_with_TMHMM_domain_list, Chromosome_to_Sequence_dict, Gene_Description_dict
elif genome == 2:
    from Making_Dictionaries_GRCh37 import ENSG_to_TMHMM_dict, ENSG_to_UniProtKb_dict, ENSG_to_Canonical_AA_dict, \
        ENSG_to_Canonical_AA_CDS_dict, genes_with_TMHMM_domain_list, Chromosome_to_Sequence_dict, Gene_Description_dict

for input_file_File_name_base_number in input_file_File_name_base_number_list:
    input_file_name = list_of_raw_files[input_file_File_name_base_number].replace(input_files_folder, "").replace(".txt", "")
    input_file_location = list_of_raw_files[input_file_File_name_base_number]
    print("\nWe're now working on " + input_file_name)
    # Make directories and files
    if not path.exists(file_folder + "/Output/"):
        makedirs(file_folder + "/Output/")
    if not path.exists(file_folder + "/Output/" + input_file_name):
        makedirs(file_folder + "/Output/" + input_file_name)
    Output_folder = file_folder + "/Output/" + input_file_name + "/"
    Output = Output_folder + input_file_name + "_All.txt"
    Filtered = Output_folder + input_file_name + "_Filtered.txt"
    Annotated_matched_genes_output_extracellular = Output_folder + input_file_name + "_Extracellular_Cassette.txt"
    Manual_annotate_output = Output_folder + input_file_name + "_Manual_Annotate.txt"
    Summary_table_output = Output_folder + input_file_name + "_Summary.txt"
    does_file_exist(Output)
    does_file_exist(Annotated_matched_genes_output_extracellular)
    does_file_exist(Manual_annotate_output)
    does_file_exist(Summary_table_output)
    dataDict = defaultdict(list)
    psiDict = defaultdict(list)
    with open(input_file_location, "rU") as rMATS_file, \
            open(input_file_location, "r") as initial_data:
        initial_data_pd = pd.read_csv(initial_data, delimiter="\t")
        rMATS_cols = list(initial_data_pd.columns.values)
        sample_names = "\t".join(rMATS_cols[10:])
        reader = DictReader(rMATS_file, delimiter="\t")
        for row in reader:
            for col, data in row.items():
                # Separate information from PSI values (starting row 10)
                if col in rMATS_cols[:10]:
                    dataDict[col].append(data)
                else:
                    psiDict[col].append(data)

    # Assign index to each hit
    gene_id = range(0, len(initial_data_pd))

    # Remove ".#" trailing ENSG
    print("\nGetting ENSGs...")
    dataDict['ENSG'] = [ENSG.partition(".")[0] for ENSG in dataDict['AC']]

    # Map to gene description from dictionary
    print("\nGetting gene descriptions...")
    dataDict['description'] = [Gene_Description_dict[ENSG].split(" [")[0] for ENSG in dataDict['ENSG']]

    # Map ENSG to UniProtKb
    print("\nGetting UniProtKb IDs...")
    dataDict['UniProtKb'] = [ENSG_to_UniProtKb_dict[ENSG][0]
                             if ENSG_to_UniProtKb_dict[ENSG] else ""
                             for ENSG in dataDict['ENSG']]

    # ENSG not mapped to any UniProtKb
    dataDict['noUP'] = [UniProtKb == "" for UniProtKb in dataDict['UniProtKb']]

    # Merge coordinates
    print("\nGetting exon coordinates...")
    dataDict['exonCoords'] = [[chromosome + ":" + exon0Start + "-" + exon0End,
                               chromosome + ":" + exon1Start + "-" + exon1End,
                               chromosome + ":" + exon2Start + "-" + exon2End]
                              for chromosome, exon0Start, exon0End, exon1Start, exon1End, exon2Start, exon2End
                              in zip(dataDict['chr'], dataDict['upstreamES'], dataDict['upstreamEE'],
                                     dataDict['exonStart'], dataDict['exonEnd'], dataDict['downstreamES'],
                                     dataDict['downstreamEE'])]

    # Get exon lengths
    print("\nGetting exon lengths...")
    dataDict['exonLengths'] = [[int(exon0End) - int(exon0Start) + 1,
                                int(exon1End) - int(exon1Start) + 1,
                                int(exon2End) - int(exon2Start) + 1]
                               for exon0End, exon0Start, exon1End, exon1Start, exon2End, exon2Start
                               in zip(dataDict['upstreamEE'], dataDict['upstreamES'], dataDict['exonEnd'],
                                      dataDict['exonStart'], dataDict['downstreamEE'], dataDict['downstreamES'])]

    # Get exon sequences from dictionary
    print("\nGetting exon sequences...")
    dataDict['exonSequences'] = [[str(Chromosome_to_Sequence_dict[chromosome][int(exon0Start):int(exon0End)]).upper(),
                                  str(Chromosome_to_Sequence_dict[chromosome][int(exon1Start):int(exon1End)]).upper(),
                                  str(Chromosome_to_Sequence_dict[chromosome][int(exon2Start):int(exon2End)]).upper()]
                                 for chromosome, exon0Start, exon0End, exon1Start, exon1End, exon2Start, exon2End
                                 in zip(dataDict['chr'], dataDict['upstreamES'], dataDict['upstreamEE'],
                                        dataDict['exonStart'], dataDict['exonEnd'], dataDict['downstreamES'],
                                        dataDict['downstreamEE'])]

    # Overwrite '-' strand sequences with reverse complement
    dataDict['exonSequences'] = [[reverse_complement(exonSequences[0]),
                                  reverse_complement(exonSequences[1]),
                                  reverse_complement(exonSequences[2])]
                                 if strand == "-" else exonSequences
                                 for exonSequences, strand in zip(dataDict['exonSequences'], dataDict['strand'])]

    # Make sure exons are in order
    print("\nQuality control:\n\tChecking exon order...")
    dataDict['exonInOrder'] = [True if int(exon0Start) < int(exon0End) <
                                       int(exon1Start) < int(exon1End) <
                                       int(exon2Start) < int(exon2End) else False
                               for exon0Start, exon0End, exon1Start, exon1End, exon2Start, exon2End
                               in zip(dataDict['upstreamES'], dataDict['upstreamEE'], dataDict['exonStart'],
                                      dataDict['exonEnd'], dataDict['downstreamES'], dataDict['downstreamEE'])]

    # Check for faulty reverse complements (upstream and downstream exons are reverse complements of each other)
    print("\tChecking for faulty reverse complements...")
    dataDict['faultyRevComp'] = [True if exonSequences[0] == reverse_complement(exonSequences[2]) else False
                                 for exonSequences in dataDict['exonSequences']]

    # Check if cassette exon inclusion/skipping with cause a frameshift because exon length is not divisible by 3
    print("\nChecking for frame shift...")
    dataDict['exon1FrameShift'] = [exonLength[1] % 3 != 0 for exonLength in dataDict['exonLengths']]

    # Map to CDS from dictionary
    print("\nGetting CDS...")
    dataDict['CDS'] = [ENSG_to_Canonical_AA_CDS_dict[ENSG + "_" + UniProtKb]
                       for ENSG, UniProtKb in zip(dataDict['ENSG'], dataDict['UniProtKb'])]

    # Map to amino acid sequence from dictionary
    print("\nGetting amino acid sequences...")
    dataDict['canonicalAA'] = [ENSG_to_Canonical_AA_dict[ENSG + "_" + UniProtKb]
                               for ENSG, UniProtKb in zip(dataDict['ENSG'], dataDict['UniProtKb'])]

    # Map to subcellular localization from dictionary
    print("\nGetting subcellular localization...")
    dataDict['subcell'] = [UniProtKb_to_Subcell_Loc_dict[UniProtKb] for UniProtKb in dataDict['UniProtKb']]

    # Map to UniProtKb topological annotation from dictionary, SLOW STEP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    print("\nGetting topology from UniProtKb...")
    dataDict['topoSrcUP'] = [UniProtKb in genes_with_topo_domain_list for UniProtKb in dataDict['UniProtKb']]

    # Extract extracellular domains from UniProtKb topological annotation dictionary
    print("\nGetting extracellular domains...")
    dataDict['extracellDomains'] = []
    for UniProtKb, topoSrcUP in zip(dataDict['UniProtKb'], dataDict['topoSrcUP']):
        if topoSrcUP:
            # Store all extracellular domains
            listExtracellDomains = []
            for extracellDomain in UniProtKb_to_Topological_Domains_dict[UniProtKb][2]:
                startPosition = extracellDomain.partition("-")[0]
                endPosition = extracellDomain.partition("-")[2]
                if "?" not in startPosition and "?" not in endPosition:
                    listExtracellDomains.append([int(startPosition), int(endPosition)])
            dataDict['extracellDomains'].append(listExtracellDomains)
        else:
            dataDict['extracellDomains'].append([])

    # Map to UniProtKb topological annotation from dictionary, SLOW STEP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    print("\nGetting topology from TMHMM...")
    dataDict['topoSrcTMHMM'] = [ENSG + "_" + UniProtKb in genes_with_TMHMM_domain_list
                                for ENSG, UniProtKb in zip(dataDict['ENSG'], dataDict['UniProtKb'])]

    # Extract extramembrane domains from TMHMM topological annotation dictionary
    print("\nGetting extramembrane domains...")
    dataDict['extramemDomains'] = []
    for ENSG, UniProtKb, topoSrcTMHMM in zip(dataDict['ENSG'], dataDict['UniProtKb'], dataDict['topoSrcTMHMM']):
        if topoSrcTMHMM:
            # Store all extramembrane domains
            listExtramemDomains = []
            for extramemDomain in ENSG_to_TMHMM_dict[ENSG + "_" + UniProtKb][2]:
                startPosition = extramemDomain.partition("-")[0]
                endPosition = extramemDomain.partition("-")[2]
                if "?" not in startPosition and "?" not in endPosition:
                    listExtramemDomains.append([int(startPosition), int(endPosition)])
            dataDict['extramemDomains'].append(listExtramemDomains)
        else:
            dataDict['extramemDomains'].append([])

    # Localize upstream and downstream exons to protein topology
    print("\nLocalizing exons to protein topology...")
    iterables = [(exonSequences[0], exonSequences[2], CDS, canonicalAA)
                 for exonSequences, CDS, canonicalAA
                 in zip(dataDict['exonSequences'], dataDict['CDS'], dataDict['canonicalAA'])]

    # Multiprocess exon alignment
    with Pool(30) as p:
        dataDict['alignment'] = p.starmap(UTR_test_and_find_best_match, iterables)

    # Get alignment scores for upstream and downstream exons
    print("\nGetting alignment scores...")
    dataDict['alignmentScores'] = [[alignment[0][0], alignment[1][0]] for alignment in dataDict['alignment']]

    # Which exon alignment does not pass the threshold
    print("\nGetting unaligned exons...")
    dataDict['notAligned'] = ["Both" if alignment[0][0] < match_threshold and alignment[1][0] < match_threshold
                              else "Upstream" if alignment[0][0] < match_threshold
    else "Downstream" if alignment[1][0] < match_threshold
    else "Aligned" for alignment in dataDict['alignment']]

    # Get amino acid positions of aligned exons [upstream end position, downstream start position]
    print("\nGetting amino acids positions of aligned exons...")
    dataDict['aaPositions'] = [[round((int(alignment[0][2]) - 1) / 3, 1),
                                round(int(alignment[1][1]) / 3, 1)] if notAligned == "Aligned"
                               else ["N/A", round(int(alignment[1][1]) / 3, 1)] if notAligned == "Upstream"
    else [round((int(alignment[0][2]) - 1) / 3, 1), "N/A"] if notAligned == "Downstream"
    else ["N/A", "N/A"]
                               for alignment, notAligned in zip(dataDict['alignment'], dataDict['notAligned'])]

    # Localize cassette exon to extracellular/membrane domain if upstream/downstream exons aligned
    print("\nLocalizing cassette exons to extracellular domain...")
    dataDict['matchedExonUP'] = [localizeCassetteExon(aaPositions[0], aaPositions[1], extracellDomains, notAligned)
                                 for aaPositions, extracellDomains, notAligned
                                 in zip(dataDict['aaPositions'], dataDict['extracellDomains'], dataDict['notAligned'])]

    print("\nLocalizing cassette exons to extramembrane domain...")
    dataDict['matchedExonTMHMM'] = [localizeCassetteExon(aaPositions[0], aaPositions[1], extramemDomains, notAligned)
                                    for aaPositions, extramemDomains, notAligned
                                    in
                                    zip(dataDict['aaPositions'], dataDict['extramemDomains'], dataDict['notAligned'])]

    # Check for upstream and downstream exon alignment to UTR
    print("\nQuality control:\n\tChecking for localization to untranslated region...")
    dataDict['UTR'] = [alignment[0][4] or alignment[1][3] for alignment in dataDict['alignment']]

    # Check if upstream and downstream exons align to the same CDS
    print("\tChecking for exon alignment to the same CDS...")
    dataDict['misalignedCDS'] = [alignment[0][5] != alignment[1][5] for alignment in dataDict['alignment']]

    # Sort hits for extracellular output file
    print("\nClassifying extracellular annotation hits...")
    dataDict['extracellular'] = [
        True if (((not topoSrcUP and UniProtKb in missing_topo_domain_gene_list and topoSrcTMHMM) or topoSrcUP)
                 and (matchedExonUP != "N/A" or matchedExonTMHMM != "N/A")) else False
        for topoSrcUP, topoSrcTMHMM, UniProtKb, matchedExonUP, matchedExonTMHMM
        in zip(dataDict['topoSrcUP'], dataDict['topoSrcTMHMM'], dataDict['UniProtKb'],
               dataDict['matchedExonUP'], dataDict['matchedExonTMHMM'])]

    # Sort hits for manual annotation output file
    print("\nClassifying manual annotation hits...")
    dataDict['manual'] = [True if not topoSrcUP and ((UniProtKb in missing_topo_domain_gene_list and not topoSrcTMHMM)
                                                     or (UniProtKb not in missing_topo_domain_gene_list and topoSrcTMHMM
                                                         and (matchedExonUP != "N/A" and matchedExonTMHMM != "N/A")))
                          else False
                          for topoSrcUP, topoSrcTMHMM, UniProtKb, matchedExonUP, matchedExonTMHMM
                          in zip(dataDict['topoSrcUP'], dataDict['topoSrcTMHMM'], dataDict['UniProtKb'],
                                 dataDict['matchedExonUP'], dataDict['matchedExonTMHMM'])]

    # BLAST to RefSeq human protein database to identify isoforms displaying splicing pattern
    print("\nGetting candidate transcripts for extracellular hits...")
    iterables = [(exonSequences[0], exonSequences[1], exonSequences[2], strand, index, 0.0001, 30) if extracellular
                 else ('', '', '', '', index, 0, 0)
                 for exonSequences, strand, index, extracellular
                 in zip(dataDict['exonSequences'], dataDict['strand'], gene_id, dataDict['extracellular'])]

    # Multiprocess BLAST
    with Pool(100) as p:
        dataDict['isoforms'] = p.starmap(findIsoform, iterables)

    # Filter out unwanted hits
    full = pd.DataFrame.from_dict(dataDict)
    # Exons cannot align to UTR
    a = full['UTR'] == False
    # Exons must align to same CDS
    b = full['misalignedCDS'] == False
    # Exons must be in order
    c = full['exonInOrder'] == True
    # Upstream and downstream exons cannot be faulty reverse complemenets
    d = full['faultyRevComp'] == False
    # Transcript must be mapped to a UniProtKb entry
    e = full['noUP'] == False
    # Transcript must be mapped to a CDS
    f = full['CDS'] != ""
    # Upstream and downstream exons cannot both be unaligned to CDS
    g = full['notAligned'] != "Both"

    # Filter to specific output files
    h = full['extracellular'] == True
    i = full['manual'] == True

    # Count hits not discarded
    countNotA = len(initial_data_pd) - sum(a)
    countNotB = len(initial_data_pd) - sum(b)
    countNotC = len(initial_data_pd) - sum(c)
    countNotD = len(initial_data_pd) - sum(d)
    countNotE = len(initial_data_pd) - sum(e)
    countNotF = len(initial_data_pd) - sum(f)
    countNotG = len(initial_data_pd) - sum(g)

    # Separate extracellular and manual outputs
    filtered = full[a & b & c & d & e & g]
    extracell = full[a & b & c & d & e & g & h]
    manual = full[a & b & c & d & e & g & i]

    # Only keep relevant columns
    keyList = ['ENSG', 'GeneName', 'description', 'UniProtKb', 'strand', 'exonCoords', 'upstreamES', 'upstreamEE',
               'exonStart', 'exonEnd', 'downstreamES', 'downstreamEE', 'exonLengths', 'subcell', 'exon1FrameShift',
               'topoSrcUP', 'topoSrcTMHMM', 'aaPositions', 'extracellDomains', 'extramemDomains', 'alignmentScores',
               'matchedExonUP', 'matchedExonTMHMM', 'extracellular', 'manual', 'isoforms']
    full2 = full[keyList]
    filtered2 = filtered[keyList]
    extracell2 = extracell[keyList]
    manual2 = manual[keyList]

    # Convert PSI values into dataframe
    psiDf = pd.DataFrame.from_dict(psiDict)
    filteredPsi = psiDf.loc[filtered2.index]
    extracellPsi = psiDf.loc[extracell2.index]
    manualPsi = psiDf.loc[manual2.index]

    # Append PSI dataframe to annotation output
    full3 = pd.concat([full2, psiDf], axis=1)
    filtered3 = pd.concat([filtered2, filteredPsi], axis=1)
    extracell3 = pd.concat([extracell2, extracellPsi], axis=1)
    manual3 = pd.concat([manual2, manualPsi], axis=1)

    # Name first column (indices)
    full3.index.name = "ID"
    filtered3.index.name = "ID"
    extracell3.index.name = "ID"
    manual3.index.name = "ID"

    # Write outputs
    print("\nWriting outputs...\n")
    full3.to_csv(Output, sep="\t")
    filtered3.to_csv(Filtered, sep="\t")
    extracell3.to_csv(Annotated_matched_genes_output_extracellular, sep="\t")
    manual3.to_csv(Manual_annotate_output, sep="\t")

    # Output summary statistics
    summary_rMATS_count = len(initial_data_pd)
    summary_ENSG_count = len(set(full['ENSG']))
    summary_kept_count = len(filtered)
    summary_discard_count = summary_rMATS_count - summary_kept_count

    with open(Summary_table_output, "w") as summary_output:
        summary_output.write("Unique rMATS hits\t" + str(summary_rMATS_count) +
                             "\nUnique ENSG\t" + str(summary_ENSG_count) +
                             "\n\nHits kept for analysis\t" + str(summary_kept_count) +
                             "\n\tHits as extracellular cassette exons\t" + str(sum(h)) +
                             "\n\tHits that require manual annotation\t" + str(sum(i)) +
                             "\n\nHits discarded from analysis\t" + str(summary_discard_count) +
                             "\n\tHits tossed because exons out of order\t" + str(countNotC) +
                             "\n\tHits tossed as faulty reverse complements\t" + str(countNotD) +
                             "\n\tHits tossed because no UniProtKb ID\t" + str(countNotE) +
                             "\n\tHits tossed because didn't have an associated CDS\t" + str(
            countNotF) +
                             "\n\tHits tossed because couldn't be aligned to a CDS that was matched to UniProt's canonical sequence\t" + str(
            countNotG) +
                             "\n\tHits tossed cassette exon is in UTR\t" + str(countNotA) +
                             "\n\tHits tossed because exons aligned to different CDS\t" + str(countNotB))

