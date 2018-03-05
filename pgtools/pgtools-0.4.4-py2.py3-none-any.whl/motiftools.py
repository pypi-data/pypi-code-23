import os
import bs4
import numpy
import scipy
import pandas
import math
import re
import datetime
import collections
import statsmodels.sandbox.stats.multicomp
from Bio.motifs._pwm import calculate as biopython_motif_calculate

from pgtools import toolbox

BACKGROUND_FREQUENCY_FILENAME = toolbox.home_path('model_data/background_nucleotide_frequencies.csv')


def get_background_frequencies(genome_build, background_frequency_fname=BACKGROUND_FREQUENCY_FILENAME):
    updated = False

    print('Loading background nucleotide frequencies from {}'.format(background_frequency_fname))
    try:
        background_models = pandas.read_csv(background_frequency_fname, index_col=0).to_dict('list')
    except (IOError, OSError):
        background_models = {}
        print('File not found.'.format(background_frequency_fname))
    else:
        print('Background frequencies loaded.')

    if genome_build in background_models:
        print('Found background model for genome {}: {}'.format(genome_build, background_models[genome_build]))
    else:
        print('\tBackground frequencies for genome build {} not found. Computing now...'.format(
            genome_build))
        genome = genomic_tools.Genome(genome_build)
        background_models[genome_build] = genome.compute_nucleotide_frequencies()
        updated = True
        
    if updated:
        print('Saving updated background nucleotide frequencies to {}'.format(background_frequency_fname))
        pandas.DataFrame(background_models).to_csv(background_frequency_fname)
        
    return background_models[genome_build]

    
def generate_random_sequence(size, nucleotide_frequencies=[0.25]*4, random_seed=None):
    """
    Returns a string of random nucleotides of length :param:`size` drawn from the distribution
    specified by :param:`nucleotide_frequencies`. 
    """
    numpy.random.seed(random_seed)
    return ''.join(numpy.random.choice(['A', 'C', 'G', 'T'], size=size, p=nucleotide_frequencies))

###############################################################################
## Motif classes    
###############################################################################

# ToDo: add in k-nucleotide attributes and conversion methods.
class Motif():
    """
    Parent class for motif instances.
    """
    CHARS_TO_REMOVE = '[|]ACGT'

    def __repr__(self):
        return self.data.__repr__()
    
    def __str__(self):
        return self.data.__str__()
    
    @property
    def motif_width(self):
        return self.data.shape[1]
    
    @classmethod
    def _parse_horizontal_motif(cls, matrix_string_list, dtype):
        assert len(matrix_string_list) == 4

        # Peek at the first line to detect number of columns
        split_line = re.split(toolbox.WHITESPACE, toolbox.replace_multi(matrix_string_list[0], cls.CHARS_TO_REMOVE, '').strip())
        num_columns = len(split_line)

        matrix = numpy.zeros((4, num_columns), dtype=dtype)
        for matrix_row, line in enumerate(matrix_string_list):
            split_line = re.split(toolbox.WHITESPACE, toolbox.replace_multi(line, cls.CHARS_TO_REMOVE, '').strip())
            assert len(split_line) == num_columns, 'Found {} columns on row {}, expected {}'.format(len(split_line), matrix_row, num_columns)
            matrix[matrix_row, :] = numpy.array([dtype(element) for element in split_line])

        return matrix
    
    @classmethod
    def _parse_vertical_motif(cls, matrix_string_list, dtype):
        num_rows = len(matrix_string_list)

        matrix = numpy.zeros((4, num_rows), dtype=dtype)
        for matrix_row, line in enumerate(matrix_string_list):
            if line != '':
                split_line = re.split(toolbox.WHITESPACE, toolbox.replace_multi(line, cls.CHARS_TO_REMOVE, '').strip())
                assert len(split_line) == 4, 'Found {} columns on row {}, expected 4'.format(len(split_line), matrix_row)
                matrix[:, matrix_row] = numpy.array([dtype(element) for element in split_line])
        return matrix    
    
    @staticmethod
    def _read_multi_motif_file(multi_motif_filename):
        """
        Reads the contents of :param:`motif_filename` that contains motif matrices separated by FASTA-style
        headers (lines starting with '>") and returns a dictionary of lists of lines keyed by header contents.
        
        These lines can be then passed to parsing functions to convert them to motif matrices.
        """
        lines_dict = collections.OrderedDict()
        with open(multi_motif_filename, 'rt') as multi_motif_file:
            these_lines = []
            
            for line in multi_motif_file:
                line = line.strip()
                if line:
                    if line.startswith('>'):  # header line
                        if these_lines:
                            assert header not in lines_dict, 'Encountered duplicate entry for motif {} !'.format(header)                            
                            lines_dict[header] = these_lines
                            these_lines = []
                        header = line[1:].strip()
                    else:
                        these_lines.append(line.strip())
                        
            lines_dict[header] = these_lines
            
        return lines_dict
    
    def rev_complement(self):
        """
        Retruns the reverse complement of a motif (either PWM or PFM) by reversing the order and transposing A/T and C/G.
        :param motif_matrix: A 2D matrix with nucleotides in rows in alpha order A,C,G,T and positions in columns
        :return:  A 2D matrix with nucleotides in rows in alpha order A,C,G,T and positions in columns
        """
        return self.data[(3, 2, 1, 0), ::-1]
    
    
class Pcm(Motif):
    def __init__(self, pcm_matrix):
        """
        """
        assert pcm_matrix.dtype == int, 'Received invalid dtype {} for pcm_matrix, was expecting int'.format(pcm_matrix.dtype)
        pcm_matrix = numpy.array(pcm_matrix, dtype=int)
        self.data = pcm_matrix
             
    @classmethod
    def from_strings(cls, pcm_strings, orientation='horiz'):
        if orientation == 'horiz':
            return cls(cls._parse_horizontal_motif(pcm_strings, dtype=int))
        elif orientation == 'vert':
            return cls(cls._parse_vertical_motif(pcm_strings, dtype=int))  

    @classmethod
    def from_file(cls, pcm_filename, orientation='horiz'):
        with open(pcm_filename, 'rt') as in_file:
            pcm_strings = in_file.readlines()
        if pcm_strings[0].startswith('>'):
            pcm_strings = pcm_strings[1:]

        return cls.from_strings(pcm_strings=pcm_strings, orientation=orientation)            
    
    def to_pfm(self, pseudocount=0):
        """
        Converts a position count matrix (PCM) to position frequency matrix (PFM) by converting counts to frequencies
        (assume nucleotides in rows in alpha order A,C,G,T,
        transpose the input if nucleotides in columns).
        Adds <psuedo_count> to each entry before calculating.
        """
        return Pfm(((self.data + pseudocount) / self.data.sum(axis=0)).astype(float))
    
    def to_pwm(self, background_model=[0.25] * 4, pseudocount=0):
        """
        Converts a PCM to PWM by converting counts to frequencies (assume nucleotides in rows in alpha order A,C,G,T,
        transpose the input if nucleotides in columns), then calculating the log2 ratio between the matrix frequency and
        the background frequency (<background_model> should be given as a sequence of four frequencies in A,C,G,T order.)

        Adds <psuedo_count to each entry>.
        """
        return Pwm(numpy.log2(numpy.apply_along_axis(numpy.divide, 0, self.to_pfm(pseudocount).data, background_model)))
        
        
class Pfm(Motif):
    def __init__(self, pfm_matrix):
        """
        """
        pfm_matrix = numpy.array(pfm_matrix)
        assert pfm_matrix.dtype == float, 'Recieved invalid dtype {} for pfm_matrix, was expecting float'.format(pfm_matrix.dtype)
        self.data = pfm_matrix

    @classmethod
    def from_homer_strings(cls, homer_strings):
        header_line = homer_strings[0] # currently unused
        return cls._parse_vertical_motif(homer_strings[1:], dtype=float)
        
    @classmethod
    def from_strings(cls, pfm_strings, orientation='horiz'):
        if orientation == 'horiz':
            return cls(cls._parse_horizontal_motif(pfm_strings, dtype=float))
        elif orientation == 'vert':
            return cls(cls._parse_vertical_motif(pfm_strings, dtype=float))  

    @classmethod
    def from_file(cls, pfm_filename, orientation='horiz'):
        with open(pfm_filename, 'rt') as in_file:
            pfm_strings = in_file.readlines()
        if pfm_strings[0].startswith('>'):
            pfm_strings = pfm_strings[1:]

        return cls.from_strings(pfm_strings=pfm_strings, orientation=orientation)               
           
    def to_pcm(self, total_count=1000, pseudocount=0):
        """
        Converts a position frequency matrix (PFM) to a theoretical position count matrix (PCM)
        by multiplying each frequency by the specified :param:`total_count`

        (assumes nucleotides in rows in alpha order A,C,G,T,
        transpose the input if nucleotides in columns).

        Adds <psuedo_count> to each entry before calculating.
        """
        return Pcm((self.data * total_count).astype(int) + pseudocount)  
    
    def to_pwm(self, background=[0.25] * 4, pseudofrequency=0):
        """
        Converts a PFM to PWM by converting frequencies to weights (assume nucleotides in rows in alpha order A,C,G,T,
        transpose the input if nucleotides in columns), then calculating the log2 ratio between the matrix frequency and
        the background frequency (<background_model> should be given as a sequence of four weights in A,C,G,T order.)

        Adds <pseudo_frequency to each entry>.
        """
        return Pwm(numpy.log2(numpy.apply_along_axis(numpy.divide, 0, self.data + pseudofrequency, background)))

    def export_to_homer(self, motif_name, motif_filename, llr_threshold=0):
        with open(motif_filename, 'wt') as motif_file:
            motif_file.write('>{}\t{}\t{}\n'.format(''.join(consensus_sequence(self.data)), motif_name, llr_threshold))
            for col in range(self.motif_width):
                motif_file.write('{}\n'.format('\t'.join([str(x) for x in self.data[:, col]])))
                
    def entropy_by_pos(self):
        entropy_weights = numpy.zeros(self.motif_width)
        for pos in range(self.motif_width):
            for nuc in range(4):
                entropy_weights[pos] -= self.data[nuc, pos] * math.log(self.data[nuc, pos], 2)
        return entropy_weights

        
    
class Pwm(Motif):
    def __init__(self, pwm_matrix):
        """
        """
        pwm_matrix = numpy.array(pwm_matrix)
        assert pwm_matrix.dtype == float, 'Recieved invalid dtype {} for pfm_matrix, was expecting float'.format(pfm_matrix.dtype)
        self.data = pwm_matrix
        
    def export_pwm_to_meme(self, motif_name, fname, background_model, meme_version=4, strands='+'):
        """
        Placeholder stub for export to meme
        """
        with open(fname, 'wt') as out_file:
            out_file.write('MEME version {}\n'.format(meme_version))
            out_file.write('ALPHABET = ACGT\n')
            out_file.write('STRANDS: +\n')
            out_file.write('Background letter frequencies\n')
            out_file.write('A {} C {} G {} T {}\n'.format(*background_model))
            out_file.write('MOTIF {}\n'.format(motif_name))
        pass
        
    def scan_sequence(self, sequence):
        return scan_pwm(sequence, self)
        

def load_jaspar_motifs(jaspar_filename):
    """
    Assuming :param:`jaspar_filename` contains a sequence of jaspar motifs, 
    returns the contents of as a dictionary of PCMs.    
    """
    return {re.split(toolbox.WHITESPACE, key)[1]:Pcm.from_strings(lines) for key, lines in Pcm._read_multi_motif_file(jaspar_filename).items()}
    
        
def load_homer_motifs(homer_filename):
    """
    Loads the motifs found in :param:`homer_filename` and returns them as a 
    list of Pfm objects in the order in which they appear.
    """
    
    return [Pfm.from_homer_strings(lines) for lines in Pfm._read_multi_motif_file(homer_filename).values()]

    
def load_vert_motifs(motif_filename):
    """
    Loads the vertical PFMs found in :param:`motif_filename` and returns them as a 
    dictionary of Pfm objects keyed by header.
    """
    return {header:Pfm.from_strings(lines, orientation='vert') for header, lines in Pfm._read_multi_motif_file(motif_filename).items()}    
    
 
 ##############################################################################
 ## Other tools
 ##############################################################################
    
def compute_background_distribution(seq, normalize=True):
    """
    Computes the background nucleotide distribution of a sequence (essentially a 1-position PCM)
    Returns a PFM (<normalize> if you want a PFM)
    """
    background_freq = toolbox.freq(seq)
    background_pcm = numpy.array(
        [background_freq[k] for k in sorted(background_freq.keys()) if k in ('A', 'C', 'G', 'T')])
    if normalize:
        return pcm_to_pfm(background_pcm)
    else:
        return background_pcm


def exclusive_joint(prob_a, prob_b):
    """
    Returns the joint probability of (A and not B) or (B and not A)
    """
    return prob_a + prob_b - prob_a * prob_b


def binding_probabilities(energies, mu=0):
    """
    Returns a vector of binding probabilities given a single strand vector of binding energy values (such as generated by a PWM)
    and a scalar <mu> that adjusts for the free concentration of ligand (theoretically equal to ln[TF]).
    :param energies:
    :param mu:
    :return:
    """
    return 1 / (1 + numpy.exp(-energies - mu))

    
def energy_to_prob(energy_neg, energy_pos, mu):
    return exclusive_joint(binding_probabilities(energy_pos, mu), binding_probabilities(energy_neg, mu))



def consensus_sequence(horizontal_motif_matrix):
    """
    Given either a PWM or PFM in horizontal format, returns a string containing the consensus
    sequence of that motif (best-matching nucleotide at each position)
    """
    nucs = numpy.array(['A', 'C', 'G', 'T'])
    return nucs[numpy.argmax(horizontal_motif_matrix, axis=0)]


def scan_pwm(seq, pwm, score_offset=0, at_motif_midpoint=False, method='Bio'):
    """
    Given a sequence <seq> and a Pwm object,
    compute the single-stranded binding energy of the subsequence starting at each
    position. Scores are placed at the starting point of the motif subsequence unless <score_offset> is specified, in
    which case they are shifted by the given amount toward the end of the motif.
    """
    if at_motif_midpoint:
        motif_length = pwm.data.shape[1]
        motif_midpoint = motif_length / 2 - 1
        score_offset += motif_midpoint
    if method == 'Bio':
        scan = _scan_pwm_biopython(seq, pwm.data, score_offset=score_offset)
    else:
        scan = _scan_pwm_native_python(seq, pwm.data, score_offset=score_offset)
    assert len(scan) == len(seq)  # check that we didn't screw this up
    return scan


def _scan_pwm_biopython(seq, pwm, score_offset=0):
    """
    Biopython expects nucleotides in columns, but since I like to have them in rows, this function assumes rows
    and transposes the PWM that's passed to Biopython.

    Scores are placed at the starting point of the motif subsequence unless <score_offset> is specified, in
    which case they are shifted by the given amount toward the end of the motif.
    :param seq:
    :param pwm:
    :return:
    """
    motif_length = pwm.shape[1]
    score_offset = int(score_offset)
    if type(seq) == numpy.ndarray:
        scan = biopython_motif_calculate(''.join(seq), pwm.T)
    else:
        scan = biopython_motif_calculate(seq, pwm.T)
    return numpy.concatenate((numpy.zeros(score_offset), scan, numpy.zeros(motif_length - score_offset - 1)))


def _scan_pwm_native_python(seq, pwm, score_offset=0, N_score=-4.64):
    """
    Given a sequence <seq> and a PWM in log-odds format, compute the single-stranded binding energy of the subsequence starting at each
    position. Scores are placed at the starting point of the motif subsequence unless <score_offset> is specified, in
    which case they are shifted by the given amount toward the end of the motif.

    Any 'N's in the sequence will be assigned the value of <N_score>. Default is roughly equivalent to a 1/100
    probability versus a background of 1/4
    """
    nuc_dict = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    score = numpy.zeros(len(seq))
    for start_pos in range(len(seq) - pwm.shape[1]):
        for offset in range(pwm.shape[1]):
            if seq[start_pos + offset] == 'N':
                score[start_pos + score_offset] += N_score
            else:
                score[start_pos + score_offset] += pwm[nuc_dict[seq[start_pos + offset]]][offset]
    return score



def find_motifs_empirical(genome, pwm, lr_threshold=0, fdr=0.05, p_val_threshold=None):
    """
    An early attempt at motif site thresholding by empirical p-value. Not recommended.
    """
    start_time = datetime.datetime.now()
    # number the contigs
    contig_names = {contig_number:contig_name for contig_number, contig_name in enumerate(sorted(genome.contig_names))}
    contig_numbers = {contig_name:contig_number for contig_number, contig_name in enumerate(sorted(genome.contig_names))}

    rev_pwm = motif_rev_complement(pwm) # compute the reverse complement of the motif

    # build genome wide arrays: contig identity, motif score, and start location
    contig_ids_by_contig = []
    motif_scores_by_contig = []
    start_locations_by_contig = []
    strands_by_contig = []
    print('Scoring genome sequence ...')
    for contig_name in toolbox.numerical_string_sort(genome.contig_lengths.keys()):
        contig_length = genome.contig_lengths[contig_name]
        print('\tScoring contig {} ...'.format(contig_name))
        for strand in (True, False):        
            contig_ids_by_contig.append(numpy.full(shape=contig_length, fill_value=contig_numbers[contig_name], dtype=numpy.int))
            motif_scores_by_contig.append(scan_pwm(genome.get_dna_sequence(contig_name), (rev_pwm, pwm)[strand], at_motif_midpoint=False))
            start_locations_by_contig.append(numpy.arange(contig_length))
            strands_by_contig.append(numpy.full(shape=contig_length, fill_value=strand, dtype=numpy.bool))
            
    print('Concatenating results ...')
    contig_ids = numpy.concatenate(contig_ids_by_contig)
    del(contig_ids_by_contig)
    motif_scores = numpy.concatenate(motif_scores_by_contig)
    del(motif_scores_by_contig)
    start_locations = numpy.concatenate(start_locations_by_contig)
    del(start_locations_by_contig)
    strands = numpy.concatenate(strands_by_contig)
    del(strands_by_contig)

    # remove any loci with NaN scores
    print('Filtering out invalid loci ...')
    nonnan_loci = numpy.nonzero(~numpy.isnan(motif_scores))[0]
    contig_ids = contig_ids[nonnan_loci]
    motif_scores = motif_scores[nonnan_loci]
    start_locations = start_locations[nonnan_loci]
    strands = strands[nonnan_loci]
    print('\tRemoved {} out of {} loci'.format((genome.size*2) - len(nonnan_loci), (genome.size*2)))
    del(nonnan_loci)

    # Fit a normal distribution to the whole dataset prior to filtering
    print('Fitting normal distribution ...')
    data_size = len(motif_scores)
    data_mean, data_std = motif_scores.mean(), motif_scores.std()
    motif_score_distribution = scipy.stats.norm(loc=data_mean, scale=data_std)
    print('\tMotif scores have mean {:>0.2}, SD {:>0.2}'.format(data_mean, data_std))

    # threshold by likelihood ratio
    if lr_threshold is not None:
        print('Filtering by likelihood ratio > {}'.format(lr_threshold))
        candidate_mask = motif_scores > lr_threshold
        motif_scores = motif_scores[candidate_mask]
        contig_ids = contig_ids[candidate_mask]
        start_locations = start_locations[candidate_mask]
        strands = strands[candidate_mask]
        print('\tFound {} loci out of {}.'.format(len(motif_scores), data_size))

    print('Computing p-values ...')
    # Compute p-values
    p_vals = 1 - motif_score_distribution.cdf(motif_scores)
    print('\tDone.')

    # threshold by p-value
    if p_val_threshold is not None:
        initial_hit_size = len(motif_scores)
        print('Discarding hits with p-values greater than {} ...'.format(p_val_threshold))
        p_val_mask = p_vals < p_val_threshold
        p_vals = p_vals[p_val_mask]
        motif_scores = motif_scores[p_val_mask]
        contig_ids = contig_ids[p_val_mask]
        start_locations = start_locations[p_val_mask]
        strands = strands[p_val_mask]
        print('\t{} out of {} hits passed p-value cutoff'.format(len(p_vals), initial_hit_size))   
        
    print('Applying multiple testing correction ...')
    pass_fail, q_vals, dummy, dummy = statsmodels.sandbox.stats.multicomp.multipletests(p_vals, alpha=fdr, method='fdr_bh')

    print('\tFound {} hits at an FDR of {}'.format(pass_fail.sum(), fdr))
    
    print('Constructing output ...')
    q_vals = q_vals[pass_fail]
    length_cutoff = len(q_vals)
    
    # Do final sorting and thresholding.
    sort_index = numpy.argsort(motif_scores)[::-1]
    motif_scores = motif_scores[sort_index][:length_cutoff]
    contig_ids = contig_ids[sort_index][:length_cutoff]
    start_locations = start_locations[sort_index][:length_cutoff]
    strands = strands[sort_index][:length_cutoff]
    p_vals = p_vals[sort_index][:length_cutoff]
    
    strand_translate = {True:'+', False:'-'}

    output_regions = pandas.DataFrame({'contig':[contig_names[contig_num] for contig_num in contig_ids],
                                      'start': start_locations,
                                      'end': start_locations + pwm.shape[1],
                                      'strand': [strand_translate[strand] for strand in strands],
                                      'motif_lr_score': motif_scores,
                                      'p_value': p_vals,
                                      'q_value': q_vals,
                                      })[['contig', 'start','end', 'strand', 'motif_lr_score', 'p_value', 'q_value']]
                                      
    print('All done in {}'.format(datetime.datetime.now() - start_time))
    return output_regions
    

def find_motifs(sequence_dictionary, pwm, llr_threshold=0, fdr=0.05, p_val_threshold=None, polish_partition=True, initial_search_fraction=1e-7, mem_map=False):
    """
    Models the motif score distribution as a mixture of signal component defined by a PWM
    and a gaussian noise component.
    """
    # ToDo: Add KS test sanity check for agreement of background scores to background distribution.
    
    start_time = datetime.datetime.now()
    motif_width = pwm.shape[1]
    
    # number the contigs
    contig_names = {contig_number:contig_name for contig_number, contig_name in enumerate(sorted(sequence_dictionary))}
    contig_numbers = {contig_name:contig_number for contig_number, contig_name in enumerate(sorted(sequence_dictionary))}
    contig_lengths = {contig_name:len(sequence_dictionary[contig_name]) for contig_name in sequence_dictionary}
    genome_size = sum([len(sequence_dictionary[contig_name]) for contig_name in sequence_dictionary])

    rev_pwm = motif_rev_complement(pwm) # compute the reverse complement of the motif

    # build genome wide arrays: contig identity, motif score, and start location
    contig_ids_by_contig = []
    motif_scores_by_contig = []
    start_locations_by_contig = []
    strands_by_contig = []
    print('Scoring genome sequence ...')
    for contig_name in toolbox.numerical_string_sort(sequence_dictionary):
        contig_length = len(sequence_dictionary[contig_name])
        print('\tScoring contig {} ...'.format(contig_name))
        for strand in (True, False):        
            contig_ids_by_contig.append(numpy.full(shape=contig_length, fill_value=contig_numbers[contig_name], dtype=numpy.int16)[:-(motif_width -1)])
            motif_scores_by_contig.append(scan_pwm(sequence_dictionary[contig_name], (rev_pwm, pwm)[strand], at_motif_midpoint=False)[:-(motif_width -1)])
            start_locations_by_contig.append(numpy.arange(contig_length).astype(numpy.int32)[:-(motif_width -1)])
            strands_by_contig.append(numpy.full(shape=contig_length, fill_value=strand, dtype=numpy.bool)[:-(motif_width -1)])

    del(sequence_dictionary)
            
    print('Concatenating chromosomes ...')
    contig_ids = numpy.concatenate(contig_ids_by_contig)
    del(contig_ids_by_contig)
    motif_scores = numpy.concatenate(motif_scores_by_contig)
    del(motif_scores_by_contig)
    start_locations = numpy.concatenate(start_locations_by_contig)
    del(start_locations_by_contig)
    strands = numpy.concatenate(strands_by_contig)
    del(strands_by_contig)

    # remove any loci with NaN scores
    print('Filtering out invalid loci ...')
    nonnan_loci = numpy.nonzero(~numpy.isnan(motif_scores))[0]
    contig_ids = contig_ids[nonnan_loci]
    motif_scores = motif_scores[nonnan_loci]
    start_locations = start_locations[nonnan_loci]
    strands = strands[nonnan_loci]
    print('\tRemoved {} out of {} loci'.format((genome_size*2) - len(nonnan_loci), (genome_size*2)))
    del(nonnan_loci)

    print('Prioritizing ...')
    sort_index = numpy.argsort(motif_scores)[::-1]
    motif_scores = motif_scores[sort_index]
    contig_ids = contig_ids[sort_index]
    start_locations = start_locations[sort_index]
    strands = strands[sort_index]
    del(sort_index)
    
    if mem_map:
        print('Mem mapping ...')
        motif_scores = toolbox.replace_with_mem_map(motif_scores, tmp_dir=TMP_DIR)
        contig_ids = toolbox.replace_with_mem_map(contig_ids, tmp_dir=TMP_DIR)
        start_locations = toolbox.replace_with_mem_map(start_locations, tmp_dir=TMP_DIR)
        strands = toolbox.replace_with_mem_map(strands, tmp_dir=TMP_DIR)
    

    print('Computing initial partition ...')
    background_mean = motif_scores.mean()
    background_std = motif_scores.std()
    print('\tInitial background N({}, {})'.format(background_mean, background_std))
    length_cutoff = numpy.argmin(numpy.abs(motif_scores - numpy.log2(toolbox.my_normal_pdf(motif_scores,
                                                                                   mean=background_mean,
                                                                                   sigma=background_std))))

    print('\tEstimated {} true motifs.'.format(length_cutoff))
    
    if polish_partition:
        def obj_func(params):
            cutoff = int(params)

            background_scores = motif_scores[cutoff:]
            background_mean = background_scores.mean()
            background_std = background_scores.std()
            ll_background = numpy.log2(toolbox.my_normal_pdf(background_scores, mean=background_mean, sigma=background_std)).sum()
            
            true_scores = motif_scores[:cutoff]
            ll_true = true_scores.sum()
            
            ll_total = ll_background + ll_true

            print('\tcutoff {}; background N({}, {})'.format(cutoff, background_mean, background_std))
            print('\tll bkg=bkg {:>0.2}, true=true {:>0.2}, total {:>0.2}'.format(ll_background, ll_true, ll_total))

            return -ll_total
    
        initial_right_bound = length_cutoff + int(len(motif_scores) * initial_search_fraction)
        
        print('Searching for  maximum likelihood partition from {} to {} ...'.format(length_cutoff, initial_right_bound))
        length_cutoff = toolbox.binary_int_min(obj_func, bounds=(length_cutoff, initial_right_bound))
        if length_cutoff == initial_right_bound: # the true minimum may be past our cutoff
            print('Initial search failed! Extending search to whole genome ...')
            length_cutoff = toolbox.binary_int_min(obj_func, bounds=(length_cutoff, len(motif_scores)))

    print('Found {} likely true motifs'.format(length_cutoff))
    true_scores = motif_scores[:length_cutoff]
    background_scores = motif_scores[length_cutoff:]
              
    print('Fitting normal distribution to background scores ...')
    data_size = len(motif_scores)
    background_mean, background_std = background_scores.mean(), background_scores.std()                                
    background_score_distribution = scipy.stats.norm(loc=background_mean, scale=background_std)
    del(background_scores)
    print('\tBackground scores have mean {:>0.2}, SD {:>0.2}'.format(background_mean, background_std))

    print('Computing final log-likelihood ratios ...')
    llr = motif_scores - numpy.log2(toolbox.my_normal_pdf(motif_scores, mean=background_mean, sigma=background_std))
    
    if llr_threshold is not None:
        print('Finding motif hits with log-likelihood ratios greater than {} ...'.format(llr_threshold))
        llr_mask = llr > llr_threshold
        motif_scores = motif_scores[llr_mask]
        contig_ids = contig_ids[llr_mask]
        start_locations = start_locations[llr_mask]
        strands = strands[llr_mask]
        del(llr_mask)
        print('\tKept {} motif hits.'.format(len(motif_scores)))
                                                  
    print('Computing p-values ...')
    # Compute p-values
    p_vals = 1 - background_score_distribution.cdf(motif_scores)
    print('\tDone.')

    # threshold by p-value
    if p_val_threshold is not None:
        initial_hit_size = len(motif_scores)
        print('Discarding hits with p-values greater than {} ...'.format(p_val_threshold))
        p_val_mask = p_vals < p_val_threshold
        p_vals = p_vals[p_val_mask]
        motif_scores = motif_scores[p_val_mask]
        contig_ids = contig_ids[p_val_mask]
        start_locations = start_locations[p_val_mask]
        llr = llr[p_val_mask]
        strands = strands[p_val_mask]
        del(p_val_mask)
        print('\t{} out of {} hits passed p-value cutoff'.format(len(p_vals), initial_hit_size))   
        
    print('Applying multiple testing correction ...')
    pass_fail, q_vals, dummy, dummy = statsmodels.sandbox.stats.multicomp.multipletests(p_vals, alpha=fdr, method='fdr_bh')

    print('\tFound {} hits at an FDR of {}'.format(pass_fail.sum(), fdr))
    
    print('Constructing output ...')
    q_vals = q_vals[pass_fail]
    length_cutoff = len(q_vals)
    
    # Do final thresholding.
    motif_scores = motif_scores[:length_cutoff]
    contig_ids = contig_ids[:length_cutoff]
    start_locations = start_locations[:length_cutoff]
    strands = strands[:length_cutoff]
    p_vals = p_vals[:length_cutoff]
    llr = llr[:length_cutoff]
    
    strand_translate = {True:'+', False:'-'}

    output_regions = pandas.DataFrame({'contig':[contig_names[contig_num] for contig_num in contig_ids],
                                      'start': start_locations,
                                      'end': start_locations + pwm.shape[1],
                                      'strand': [strand_translate[strand] for strand in strands],
                                      'motif_score': motif_scores,
                                      'empirical_llr': llr,
                                      'p_value': p_vals,
                                      'q_value': q_vals,
                                      })[['contig', 'start','end', 'strand', 'motif_score', 'empirical_llr','p_value', 'q_value']]
                                      
    print('All done in {}'.format(datetime.datetime.now() - start_time))
    return output_regions

    
def emit_sequences(linear_probabilities, size=1, random_seed=None, alphabet=('A', 'C', 'G','T')):
    """
    Given a matrix of probabilities for each nucleotide by position, returns
    a list of sequences (as lists of characters) randomly drawn from :param:`alphabet`
    using :param:`random_seed`
    """
    numpy.random.seed(random_seed)
    return [[numpy.random.choice(alphabet, p=linear_probabilities[:,col_number]) for col_number in range(linear_probabilities.shape[1])] for i in range(size)]


def count_aligned_motifs(motif_sequence_list):
    """
    Given a list of aligned sequences (as strings), return a DataFrame of counts for each observed
    character by position.
    """
    motif_counts = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
    for motif_sequence in motif_sequence_list:
        for char_pos, char in enumerate(motif_sequence):
            motif_counts[char_pos][char] += 1
    return (pandas.DataFrame(motif_counts).sort_index(axis=0)).fillna(value=0)
    

class HomerMotifEnrichment():
    def __init__(self, homer_output_directory):
        """
        Class that wraps the html output of HOMER's motif enrichment analyses.
        """
        self.homer_output_directory = homer_output_directory
        print('Initializing data wrapper for HOMER motif enrichment analyses in {}'.format(homer_output_directory))
        
        self.known_motif_table = None
        self.denovo_motif_table = None
        
        known_motif_fname = os.path.join(self.homer_output_directory, 'knownResults.html')
        denovo_motif_fname = os.path.join(self.homer_output_directory, 'homerResults.html')
        
        if os.path.isfile(known_motif_fname):
            print('Found known motif enrichments. Loading ...')
            self.known_motif_table = self._known_motifs_to_df(self._parse_known_motifs(known_motif_fname))
        
        if  os.path.isfile(denovo_motif_fname):
            print('Found de novo motif enrichments. Loading ...')
            self.denovo_motif_table = self._denovo_motifs_to_df(self._parse_denovo_motifs(denovo_motif_fname))
            self.denovo_pfms = self._load_denovo_pfms(os.path.join(self.homer_output_directory, 'homerResults'), range(self.denovo_motif_table.shape[0]))

    def _parse_known_motifs(self, known_motif_file_name):
        table_data = {}
    #     known_motif_file_name = os.path.join(motif_dir, 'knownResults.html')

        with open(known_motif_file_name, 'rt') as html_file:
            known_motifs = bs4.BeautifulSoup(html_file.read(), 'html.parser')

            table_body = known_motifs.table
            table_rows = table_body.find_all('tr')
            header_row = table_rows[0]
            col_headers = [ele.contents[0].encode() for ele in header_row.find_all('td')]
            for rank, row in enumerate(table_rows[1:]):
                new_row_data = {}
                for field_name, field_value in zip(col_headers, row.find_all('td')):
                    field_name = field_name.decode()
                    if field_value.findChildren():
                        if field_name == 'Motif':
                            # new_row_data['Motif'] = field_value.findChildren()[0].attrs['src'] # used to store the filename of the PNG in older HOMER versions. Now obsolete.
                            new_row_data['Motif'] = field_value # for now we just store the SVG markup until we figure out what to do with it.
                    else:
                        new_value = field_value.contents[0].strip()
                        if field_name == 'Name':
                            new_value = new_value.split('/')[0]
                        new_row_data[field_name] = toolbox.smart_convert(new_value)

                table_data[rank] = new_row_data
            return table_data

    def _known_motifs_to_df(self, motif_data_dict):
        COL_ORDER = ['Name',
                     'P-value',
                     'q-value (Benjamini)',
                     '% of Targets Sequences with Motif',
                     '% of Background Sequences with Motif',
                     '# Target Sequences with Motif',
                     '# Background Sequences with Motif'
                     ]
        motif_df = pandas.DataFrame(motif_data_dict).T
        motif_df = motif_df.loc[:, COL_ORDER]
        return motif_df

    def _parse_denovo_motifs(self, de_novo_motif_file_name):

        table_data = {}

        with open(de_novo_motif_file_name, 'rt') as html_file:
            known_motifs = bs4.BeautifulSoup(html_file.read(), 'html.parser')

            table_body = known_motifs.table
            table_rows = table_body.find_all('tr')
            header_row = table_rows[0]
            col_headers = [ele.contents[0].encode() for ele in header_row.find_all('td')]
    #         print col_headers
            for rank, row in enumerate(table_rows[1:]):
                new_row_data = {}
                for field_name, field_value in zip(col_headers, row.find_all('td')):
                    field_name = field_name.decode()
                    if field_value.findChildren():
                        if field_name == 'Motif':
                            # new_row_data['Motif'] = field_value.findChildren()[0].attrs['src'] # used to store the filename of the PNG in older HOMER versions. Now obsolete.
                            new_row_data['Motif'] = field_value # for now we just store the SVG markup until we figure out what to do with it.

                        elif field_name == 'Best Match/Details':
                            best_match_text = field_value.get_text()
                            matching_motif_name = best_match_text.split('/')[0]
                            similarity = float(best_match_text.split('/')[-1].split('(')[-1].split(')')[0])
                            new_row_data['Best Match'] = matching_motif_name
                            new_row_data['Similarity'] = similarity
                    else:  
                        new_value = field_value.contents[0].strip()                
                        new_row_data[field_name] = toolbox.smart_convert(new_value)

                table_data[rank] = new_row_data

            return table_data

    def _denovo_motifs_to_df(self, motif_data_dict):
        COL_ORDER = ['Best Match',
                     'Similarity',
                     'P-value',
                     '% of Targets',
                     '% of Background',
                     'STD(Bg STD)'
    #                  'Best Match/Details'
                     ]
        motif_df = pandas.DataFrame(motif_data_dict).T
        motif_df = motif_df.loc[:, COL_ORDER]
        return motif_df
    
    def _load_denovo_pfms(self, motif_directory, motif_numbers):
        print('Loading PFMs for de novo motifs ...')
        pfm_dict = {}
        for motif_num in motif_numbers:
            motif_fname = os.path.join(motif_directory, 'motif{}.motif'.format(motif_num+1))
            
            pfm_dict[motif_num] = load_homer_motifs(motif_fname)[0]
        return pfm_dict
     
     
def parse_motif_name(motif_name):
    """
    Given a motif data header from HOMER, return a tuple consisting of the trimmed motif name, the motif class, and the LLR threshold
    """
    partial_name = motif_name.split('\t')[1].split('/')[0]
    motif_class = partial_name.split('(')[1].split(')')[0]
    trimmed_name = partial_name.split('(')[0]
    threshold = float(motif_name.split('\t')[2])
    return trimmed_name, motif_class, threshold    

    
def plot_known_motif_enrichments(analysis_name, basepath, dataset_names, enrichment_threshold=0,
                                 fdr=0.05, condense_to_classes=False, fig_size=(2,12),   
                                 pairs=[],
                                 cluster_cols=True, cluster_rows=True,
                                 cmap='',
                                 motifs_to_drop=None,
                                 fig_path='',
                                 pseudocount=0.01,
                                 annot=False,
                                 orientation='vertical', 
                                 robust=False):
    """
    Generates a heatmap of known motif enrichments for all folders in :param:`dataset_names`
    within :param:`basepath`.
    """
    motif_enrichments = {dataset_name:motiftools.HomerMotifEnrichment(os.path.join(basepath, dataset_name)) for dataset_name in dataset_names}
    
    if len(dataset_names) <= 2: cluster_cols=False
        
    all_known_enrichments = {}
    for dataset_name in dataset_names:
        print(dataset_name)
        dataset = motif_enrichments[dataset_name]

        motif_enrichments[dataset_name].known_motif_table = motif_enrichments[dataset_name].known_motif_table.loc[motif_enrichments[dataset_name].known_motif_table['q-value (Benjamini)'] < fdr]
        target_freq = numpy.log2(numpy.array([float(element.strip('%')) for element in dataset.known_motif_table['% of Targets Sequences with Motif']]) + pseudocount)
        background_freq = numpy.log2(numpy.array([float(element.strip('%')) for element in dataset.known_motif_table['% of Background Sequences with Motif']]) + pseudocount)
        enrichment = target_freq - background_freq
        all_known_enrichments[dataset_name] = pandas.DataFrame(enrichment,
                                                            index = dataset.known_motif_table['Name'], columns=['{}'.format(dataset_name)], dtype=float)

        all_known_enrichments[dataset_name] = all_known_enrichments[dataset_name].loc[~all_known_enrichments[dataset_name].index.duplicated()]
        all_known_enrichments[dataset_name].name=dataset_name

    all_known_enrichment_table = pandas.concat(all_known_enrichments.values(), axis=1)
#     print(all_known_enrichment_table.columns)
    all_known_enrichment_table.sort_index(axis=0, inplace=True)

    for col in all_known_enrichment_table.columns:
        all_known_enrichment_table.loc[all_known_enrichment_table[col].isnull(), col] = 0
#     print(all_known_enrichment_table.columns)
    if condense_to_classes:
        all_known_enrichment_table = condense_motif_enrichments_by_class(all_known_enrichment_table)
#     print(all_known_enrichment_table.columns)
    all_known_enrichment_table = all_known_enrichment_table.loc[:, dataset_names]
    
    if motifs_to_drop:
        for motif in motifs_to_drop:
            if motif in all_known_enrichment_table.index:
                all_known_enrichment_table.drop(motif, axis=0, inplace=True)
    
    displayed_data = all_known_enrichment_table.loc[all_known_enrichment_table.max(axis=1) > enrichment_threshold]
    
    if pairs: # given pairs of differential analyses, make the first one positive, the second one negative and combine
        for pair in pairs:
            displayed_data.loc[:,pair[0]] -= displayed_data.loc[:,pair[1]]
            displayed_data = displayed_data.drop(pair[1], axis=1)
        cmap='RdBu_r'
    else:
        cmap='YlOrRd'
    
    if orientation=='horizontal':
        displayed_data = displayed_data.T
    
#     print(displayed_data.shape)
    cm = seaborn.clustermap(displayed_data, cmap=cmap, annot=annot, figsize=fig_size, robust=robust,
                            row_cluster=cluster_rows, col_cluster=cluster_cols)
    _ = plt.setp(cm.ax_heatmap.yaxis.get_majorticklabels(), fontsize=8, rotation=0)

    
    if fig_path:
        displayed_data.to_csv(os.path.join(fig_path, '{}.tsv'.format(analysis_name)), sep='\t')
        for fig_ext in myplots.FIG_EXTS:
            plt.savefig(os.path.join(fig_path,'{}.{}'.format(analysis_name, fig_ext)), bbox_inches='tight', dpi=myplots.FIG_DPI)
            
    return all_known_enrichment_table
    
    
    
def combine_known_motif_tables(analysis_name, basepath, dataset_names,
                                 enrichment_threshold=0,
                                 fdr=0.05, condense_to_classes=False,  
                                 pairs=[],
                                 motifs_to_drop=None,
                                 pseudocount=0.01):
    """
    Generates a table of known motif enrichments for all folders in :param:`dataset_names`
    within :param:`basepath`.
    """
    motif_enrichments = {dataset_name:motiftools.HomerMotifEnrichment(os.path.join(basepath, dataset_name)) for dataset_name in dataset_names}
    
    if len(dataset_names) <= 2: cluster_cols=False
        
    all_known_enrichments = {}
    for dataset_name in dataset_names:
        dataset = motif_enrichments[dataset_name]
        print(motif_enrichments)
        motif_enrichments[dataset_name].known_motif_table = motif_enrichments[dataset_name].known_motif_table.loc[motif_enrichments[dataset_name].known_motif_table['q-value (Benjamini)'] < fdr]
        target_freq = numpy.log2(numpy.array([float(element.strip('%')) for element in dataset.known_motif_table['% of Targets Sequences with Motif']]) + pseudocount)
        background_freq = numpy.log2(numpy.array([float(element.strip('%')) for element in dataset.known_motif_table['% of Background Sequences with Motif']]) + pseudocount)
        enrichment = target_freq - background_freq
        all_known_enrichments[dataset_name] = pandas.DataFrame(enrichment,
                                                            index = dataset.known_motif_table['Name'], columns=['{}'.format(dataset_name)], dtype=float)

        all_known_enrichments[dataset_name] = all_known_enrichments[dataset_name].loc[~all_known_enrichments[dataset_name].index.duplicated()]
        all_known_enrichments[dataset_name].name=dataset_name

    all_known_enrichment_table = pandas.concat(all_known_enrichments.values(), axis=1)
    all_known_enrichment_table.sort_index(axis=0, inplace=True)

    for col in all_known_enrichment_table.columns:
        all_known_enrichment_table.loc[all_known_enrichment_table[col].isnull(), col] = 0
    if condense_to_classes:
        all_known_enrichment_table = condense_motif_enrichments_by_class(all_known_enrichment_table)

    all_known_enrichment_table = all_known_enrichment_table.loc[:, dataset_names]
    
    if motifs_to_drop:
        for motif in motifs_to_drop:
            if motif in all_known_enrichment_table.index:
                all_known_enrichment_table.drop(motif, axis=0, inplace=True)
    
    all_known_enrichment_table = all_known_enrichment_table.loc[all_known_enrichment_table.max(axis=1) > enrichment_threshold]

    return all_known_enrichment_table
    