"""
sequences.py
Manipulate sequences
"""


def translate_dna(sequence, readthrough = False, start = 0):
    """
    Translate DNA sequence to AA sequence

    :param sequence: DNA sequence (str)
    :param readthrough: Continue reading through stop codons (bool)
    :param start: Start index of DNA sequence (int)
    :return: Translated protein sequence (str)
    """
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


def reverse_complement(seq):
    """
    Reverse complement DNA sequence for '-' strand

    :param seq: DNA sequence (str)
    :return: Reverse complemented DNA sequence (str)
    """
    seq = seq.upper()
    # Complementary base pairs
    seq_dict = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    return "".join([seq_dict[base] for base in reversed(seq)])


def makeFasta(sequences):
    """
    Convert a list of sequences into fasta format

    :param sequences: List of AA sequences (list[str, ...])
    :return: Each element of sequences as an individual fasta entry (str)
    """
    output = ""
    # x = index, y = sequence
    for x, y in enumerate(sequences):
        # > index
        # sequence
        output = output + '>' + str(x) + '\n' + str(y) + '\n'
    return output
