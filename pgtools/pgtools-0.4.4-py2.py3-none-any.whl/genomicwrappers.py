import os
import datetime
import gzip
import pickle

import tables
from Bio import bgzf
import intervaltree

from . import toolbox, motiftools
from pgtools.intervaldict import IntervalDict


DEBUG = False


########################################################################################################################
# Parameters and constants
########################################################################################################################
DATA_DIRECTORY = os.path.join(os.environ['HOME'], 'model_data')

BUILD_DATA = {'hg38':{'SEQUENCE_FILE':toolbox.home_path('model_data/reference_genomes/hg38/hg38.fa.gz'),
                     'FEATURE_FILENAME':toolbox.home_path('model_data/reference_genomes/hg38/Homo_sapiens.GRCh38.84.chr.gtf.gz'),
                     'FEATURE_PICKLE_FILENAME':toolbox.home_path('model_data/reference_genomes/hg38/feature.pickle')},
              'mm10':{'SEQUENCE_FILE':toolbox.home_path('model_data/reference_genomes/mm10/mm10.fa.gz'),
                     'FEATURE_FILENAME':toolbox.home_path('model_data/reference_genomes/mm10/Mus_musculus.GRCm38.84.chr.gff3.gz'),
                     'FEATURE_PICKLE_FILENAME':toolbox.home_path('model_data/reference_genomes/mm10/feature.pickle')}}

# Feature
CHROMOSOME_DIALECT = 'ucsc'
FEATURE_SOURCES = ['ensembl_havana', 'insdc', 'ensembl']
FEATURE_TYPES = ['gene', 'mt_gene']
FEATURE_PICKLE_FILENAME = 'feature.pickle'
SUPPLEMENTAL_GENE_INFO_FILENAME = os.path.join(DATA_DIRECTORY, 'reference/feature/gene_042216.data.gz')

# Client variant
MINIMUM_VARIANT_QUALITY = 30
VARIANT_DIRECTORY = os.path.join(DATA_DIRECTORY, 'tester', 'variant')
VARIANT_FILENAME = os.path.join(VARIANT_DIRECTORY, 'variant.vcf.gz')
VARIANT_RS_ID_INDEX_FILENAME = os.path.join(VARIANT_DIRECTORY, 'rs_id_index.pickle.gz')
VARIANT_PYTABLE_FILENAME = os.path.join(VARIANT_DIRECTORY, 'variant.hdf5')
VARIANT_PYTABLE_COMPRESSOR = 'blosc'
VARIANT_PYTABLE_COMPRESSION_LEVEL = 1

# Supplemental variant
SUPPLEMENTAL_VARIANT_FILENAME = os.path.join(DATA_DIRECTORY, 'reference/variant/snp_0130.data.gz')
KNOWN_VARIANT_PYTABLE_FILENAME = os.path.join(DATA_DIRECTORY, 'reference/variant/known_variant.hdf5')
DESCRIBED_VARIANT_PYTABLE_FILENAME = os.path.join(DATA_DIRECTORY, 'reference/variant/described_variant.hdf5')
SUPPLEMENTAL_VARIANT_PYTABLE_COMPRESSOR = 'blosc'
SUPPLEMENTAL_VARIANT_PYTABLE_COMPRESSION_LEVEL = 9

REPORTING_INTERVAL = 10000

PROMOTER_UPSTREAM = 500
PROMOTER_DOWNSTREAM = 500


def dbg_print(text=''):
    """
    Selective print: only outputs when global constant DEBUG is True
    :param text:
    :return:
    """
    if DEBUG:
        print(text)


########################################################################################################################
# Custom exceptions for communicating query errors
########################################################################################################################
class ContigNotFound(Exception):
    def __init__(self, requested_contig, valid_contigs, message=''):
        """
        Exception indicating that a contig was requested which does not exist in the genome.
        :param requested_contig:
        :param valid_contigs:
        :param message:
        """
        if not message:
            message = 'Contig {} not found. Valid contigs: {}'.format(requested_contig, ', '.join(valid_contigs))
        self.requested_contig = requested_contig
        self.valid_contigs = valid_contigs
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class GeneNotFound(Exception):
    def __init__(self, requested_gene, message=''):
        """
        Exception indicating that a gene was requested which does not exist in the genome.
        :param requested_gene:
        :param message:
        """
        if not message:
            message = 'Gene {} not found'.format(requested_gene)
        self.requested_gene = requested_gene
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class VariantNotFound(Exception):
    def __init__(self, requested_variant, message=''):
        """
        Exception indicating that the requested variant was not found in the resource (whether client variants,
         described variants, or known variants)
        :param requested_variant:
        :param message:
        """
        if not message:
            message = 'Variant {} not found'.format(requested_variant)
        self.requested_variant = requested_variant
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

def validate_coordinates(start, end, current_contig, valid_range):
    """
    Convenience function to automatically check for problems with coordinates and raise the appropriate exceptions
    """
    if start < valid_range[0]:
        raise CoordinateOutOfBounds(problematic_coordinate=start,
                                    problem_with_start=True,
                                    coordinate_too_small=True,
                                    valid_coordinate_range=valid_range,
                                    current_contig=current_contig)
    if start > valid_range[1]:
        raise CoordinateOutOfBounds(problematic_coordinate=start,
                                    problem_with_start=True,
                                    coordinate_too_small=False,
                                    valid_coordinate_range=valid_range,
                                    current_contig=current_contig)
    if end < valid_range[0]:
        raise CoordinateOutOfBounds(problematic_coordinate=end,
                                    problem_with_start=False,
                                    coordinate_too_small=True,
                                    valid_coordinate_range=valid_range,
                                    current_contig=current_contig)
    if end > valid_range[1]:
        raise CoordinateOutOfBounds(problematic_coordinate=end,
                                    problem_with_start=False,
                                    coordinate_too_small=False,
                                    valid_coordinate_range=valid_range,
                                    current_contig=current_contig)
    if end <= start:
        raise InvalidCoordinates(start=start, end=end)


class CoordinateOutOfBounds(Exception):
    def __init__(self, problematic_coordinate, problem_with_start, coordinate_too_small, valid_coordinate_range,
                 current_contig, message=''):
        """
        One of the requested genome coordinates is either below 0 or greater than the size of the current contig.

        A pair of boolean variables indicates which sub-condition is active:
        if problem_with_start, it's the start coordinate, otherwise the end
        if coordinate_too_small, it's too small, otherwise it's too big.

        :param message:
        :param problem_with_start:
        :param coordinate_too_small:
        :param valid_coordinate_range:
        :return:
        """
        self.problematic_coordinate = problematic_coordinate
        self.problem_with_start = problem_with_start
        self.coordinate_too_small = coordinate_too_small
        self.valid_coordinate_range = valid_coordinate_range
        self.current_contig = current_contig

        if not message:
            if self.problem_with_start:
                message = 'Start'
            else:
                message = 'End'
            message += ' coordinate {} is too '.format(problematic_coordinate)

            if self.coordinate_too_small:
                message += 'small.'
            else:
                message += 'big.'

            message += ' Valid coordinates: [{}, {})'.format(valid_coordinate_range[0], valid_coordinate_range[1])

        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class InvalidCoordinates(Exception):
    def __init__(self, start, end, message=''):
        """
        Handles all coordinate problems not captured by CoordinateOutOfBounds. Currently only implements
        the situation where the start is after the end.

        :param start:
        :param end:
        :param message:
        :return:
        """
        self.start = start
        self.end = end
        if not message:
            message = 'Start coordinate >= end coordinate'

        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class InvalidStrandValue(Exception):
    def __init__(self, requested_strand, valid_strands=(-1, 1), message=''):
        """
        Exception indicating that an invalid strand value has been passed
        :param requested_strand:
        :param message:
        """
        if not message:
            message = 'Invalid strand: {}. Allowable values: {}'.format(requested_strand, ', '.join(valid_strands))
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.requested_strand = requested_strand

        
########################################################################################################################
# Utility functions
########################################################################################################################

def find_file_gzipped(base_filename, file_mode='rt'):
    """
    Look first for a gzipped version of a file, then a plaintext version,
    and return a file handle if successful, and None if not.

    :param base_filename:
    :param file_mode:
    :return:
    """
    try:
        return gzip.open(base_filename + '.gz', file_mode)
    except (IOError, OSError):
        try:
            return open(base_filename, file_mode)
        except (IOError, OSError):
            return None


def bgzip_and_tabix(bed_filename):
    """
    Compress and index :param:`bed_filename` using bgzip and tabix.
    """
    subprocess.run(['bgzip', bed_filename])
    compressed_filename = bed_filename + '.gz'
    subprocess.run(['tabix', '-s', '1', '-b', '2', '-e', '3', '-f', compressed_filename])


def convert_gzipped_to_bgzipped(gzipped_filename):
    """
    Convert :param:`gzipped_filename` into a bgzipped file with the same name.
    """
    # path, fname, extension = parse_path(gzipped_filename)
    temp_filename = gzipped_filename + '_temp'
    with gzip.open(gzipped_filename, 'rt') as gzipped_file:
        with bgzf.open(temp_filename, 'wt') as temp_bgzipped_file:
            for line in gzipped_file:
                temp_bgzipped_file.write(line)
    os.remove(gzipped_filename)
    os.rename(temp_filename, gzipped_filename)
    
    
def parse_gff3(feature_filename, sources=FEATURE_SOURCES, types=FEATURE_TYPES):
    """
    Parse and return 1) a dictionary of features keyed by IDs and 2) a dictionary mapping features to IDs
    """
    sources = set(sources)
    types = set(types)

    features, feature_to_id = {}, {}

    for line_num, line in enumerate(feature_filename):
        # Parse non-headers
        if line[0] != '#':
            split_line = line.split('\t')
            if len(split_line) < 7:
                dbg_print('Column error on line {}: {}'.format(line_num, split_line))

            source, feature_type = split_line[1], split_line[2]

            # If both the source and type match
            if source in sources and feature_type in types:
                contig = convert_chromosome(split_line[0], CHROMOSOME_DIALECT)
                start = int(split_line[3])
                end = int(split_line[4])
                
                if split_line[6] == '+':
                    strand = 1
                elif split_line[6] == '-':
                    strand = -1
                else:
                    strand = 0

                fields = dict(field_value_pair.split('=') for field_value_pair in split_line[8].split(';'))
                version = float(fields['version'])
                gene_name = fields['Name']
                ensembl_id = fields['gene_id']
                # Make sure not duplicated ensembl IDs
                assert ensembl_id not in features

                features[ensembl_id] = {'contig': contig,
                                        'start': start - 1,  # convert 1-based to 0-based
                                        'end': end,
                                        # convert 1-based to 0-based and account for fully-closed interval of GFF (they cancel out)
                                        'strand': strand,
                                        'version': version,
                                        'gene_name': gene_name,
                                        'ensembl_id': ensembl_id}

                # Save a new feature or an existing feature with an an updated version
                if gene_name not in feature_to_id or version > features[ensembl_id]['version']:
                    feature_to_id[gene_name] = ensembl_id

    return features, feature_to_id

    
def convert_chromosome(chromosome, dest='ensembl'):
    """
    Interconverts chromosome names from UCSC or Ensembl to the dialect specified by :param:`dest`

    :param chromosome:
    :param dest:
    :return:
    """
    if dest == 'ensembl':
        if chromosome == 'chrM':
            return 'MT'
        elif chromosome[:3].lower() == 'chr':
            return chromosome[3:]
        else:
            return chromosome
            
    elif dest == 'ucsc':
        if chromosome == 'MT':
            return 'chrM'
        elif chromosome[:3].lower() == 'chr':
            return chromosome
        else:
            return 'chr{}'.format(chromosome)
    else:
        raise ValueError('Unknown destination {}'.format(dest))   
    
    
def parse_gtf(feature_filename, sources=FEATURE_SOURCES, types=FEATURE_TYPES):
    """
    Parse <feature_filename> and return 1) a dictionary of features keyed by IDs and 2) a dictionary mapping features to IDs

    :param feature_filename:
    :param sources:
    :param types:
    :return:
    """
    types = set(types)

    features, feature_to_id = {}, {}

    for line_num, line in enumerate(feature_filename):
        # Parse non-headers
        if line[0] != '#':
            split_line = line.strip().split('\t')
            if len(split_line) < 7:
                dbg_print('Column error on line {}: {}'.format(line_num, split_line))

            feature_type = split_line[2]

            # If the type matches
            if feature_type in types:
                fields = dict([field_value_pair.strip().split(' ') for field_value_pair in split_line[8].split(';')
                               if len(field_value_pair) > 0])

                # If the source match
                if fields['gene_source'].strip('"') in sources:
                    contig = convert_chromosome(split_line[0], CHROMOSOME_DIALECT)
                    start = int(split_line[3])
                    end = int(split_line[4])
                    if split_line[6] == '+' or split_line[6] == '0':
                        strand = 0
                    elif split_line[6] == '-' or split_line[6] == '1':
                        strand = 1
                    else:
                        raise ValueError('Invalid strand value {}'.format(split_line[6]))

                    gene_name = fields['gene_name'].strip('"')
                    ensembl_id = fields['gene_id'].strip('"')
                    # Make sure not duplicated ensembl IDs
                    assert ensembl_id not in features

                    features[ensembl_id] = {'contig': contig,
                                            'start': start,
                                            'end': end,
                                            'strand': strand,
                                            'gene_name': gene_name,
                                            'ensembl_id': ensembl_id}

                    if gene_name not in feature_to_id:
                        feature_to_id[gene_name] = ensembl_id

    return features, feature_to_id 
    

########################################################################################################################
# Classes for wrapping genome data
########################################################################################################################
        
class GenomeSequence(object):
    """
    Wrapper around a single FASTA file that has been compressed with block gzip (bgzip), a utility
    that accompanies samtools. Block gzip allows fast random access to 64 kb segments of the compressed
    file. This class implements the loading, saving and generation of an index to permit identification
    of the blocks containing the sequence of any arbitrary region of the genome. It also implements
    methods to decompress and return that sequence.

    I used the bgzf module in order to determine determine the file intervals of the compressed blocks. Then I go
    through the file and find the contig intervals in terms of the file offsets. Next I match compressed blocks to
    contigs based on their overlapping file intervals. Then I convert the block file coordinates to sequence
    coordinates using the offset conversion code (need to subtract 1 for the newline character on each line).

    Now we have an interval tree for each contig giving the start position of each compressed block that contains part
    of the sequence, and what part of the sequence it contains.

    So to query, we use the interval tree for the requested contig to get the coordinates of the compressed block
    containing the sequence start position and compute the offset of the start position within that block. Now we can
    use the bgzf code to seek directly to that spot and then read until we have the requested sequence.

    This solution is:
    * Pretty damn fast (blocks can be found in O(log N), and minimum decompression operation is now only 64 kb)
    * Disk space efficient (sequence is stored compressed on disk).
    * Memory efficient (all the unrequested sequence stays on disk, and since the index consists only of one entry per
     block (~48K of them), it has a very small memory footprint).
    """

    def __init__(self, bgzipped_fasta_filename, force_rebuild=False):
        """
        Create a new object with no index

        :param bgzipped_fasta_filename:
        :return:
        """
        self.bgzipped_fasta_filename = bgzipped_fasta_filename
        self._contig_lengths = {}
        self._index = {}

        contig_length_filename = self.bgzipped_fasta_filename + '_contig_length.txt'
        index_filename = self.bgzipped_fasta_filename + '_index.gz'

        if not force_rebuild:
            try:
                self.load_contig_lengths(contig_length_filename)
            except (IOError, OSError, ValueError, EOFError):
                force_rebuild = True
        if not force_rebuild:
            try:
                self.load_index_from_text(index_filename)
            except (IOError, OSError, ValueError, EOFError):
                force_rebuild = True

        if force_rebuild:
            self.generate_index()
            self.save_contig_lengths(contig_length_filename)
            self.save_index_to_text(index_filename)

    @property
    def contig_names(self):
        """
        Read only property returning a list of the names of each contig in the genome.
        :return:
        """
        return toolbox.numerical_string_sort(self._contig_lengths.keys())

    @property
    def contig_lengths(self):
        """
        Read only property returning a dictionary containing  the length (in base pairs) of each contig in the genome
        :return:
        """
        return self._contig_lengths.copy()

    def trim_contigs(self, keep_sex=True):
        """
        Removes any contigs that have an 'Un', an underscore, 'MT' or 'random' in the name.
        
        If :param:`keep_sex` is False, additionally remove any X, Y, Z or W chromosomes.
        
        For now assumes chromosome dialect is 'ucsc'
        """
        contig_list = self.contig_names
        for contig in contig_list:
            banned_substrings = ['_', 'Un', 'random', 'MT', 'M']
            if not keep_sex: banned_substrings += ['X', 'Y', 'Z', 'W']
            if sum([substring in contig for substring in banned_substrings]):
                del(self._contig_lengths[contig])
        
    def _text_distance_to_file_distance(self, offset_sequence):
        """
        Converts a distance from the start of a genomic sequence (or other string) into a distance from the start
         of a multi-line file (as in a FASTA).

        :param offset_sequence:
        :return:
        """
        num_lines = int(offset_sequence / self.line_length_text_distance)
        partial_line_length = offset_sequence % self.line_length_text_distance
        return num_lines * self.line_length_file_distance + partial_line_length

    def _file_distance_to_text_distance(self, offset_file_distance, sequence_start_file_distance):
        """
        Converts a distance from the start of a multi-line file string (as in a FASTA)
        into a genomic sequence (or other string) into a distance from the start of a genomic sequence (or other string).

        :param offset_file_distance: The file distance to be converted
        :param sequence_start_file_distance: The location in the file that the sequence begins
        :return:
        """
        file_distance = offset_file_distance - sequence_start_file_distance
        num_lines = int(file_distance / self.line_length_file_distance) - 1
        partial_line_length = file_distance % self.line_length_file_distance
        return num_lines * self.line_length_text_distance + partial_line_length  # for some reason we need to use file distance for both which doesn't make sense conceptually.

    def _get_blocks(self):
        """
        Return a tuple for each compressed block in the bzgipped FASTA file, consisting of
        (binary_start,file_end,file_block_start)

        :return:
        """
        start_time = datetime.datetime.now()
        dbg_print('\tFinding block boundaries ...')

        def populate_blocks():
            with open(self.bgzipped_fasta_filename, 'rb') as fasta_file_for_blocks:
                # store uncompressed data start, uncompressed data end, compressed block start as a tuple
                blocks = [(b[2], b[2] + b[3], b[0]) for b in bgzf.BgzfBlocks(fasta_file_for_blocks)]
                dbg_print('\t\tFound {} blocks in {}'.format(len(blocks), datetime.datetime.now() - start_time))
            return blocks

        try:
            blocks = populate_blocks()
        except ValueError:
            dbg_print('This does not appear to be a valid block-gzipped file. Converting now ...')
            convert_start_time = datetime.datetime.now()
            convert_gzipped_to_bgzipped(self.bgzipped_fasta_filename)
            dbg_print('\tDone in {}'.format(datetime.datetime.now() - convert_start_time))
            blocks = populate_blocks()

        return blocks[:-1]  # omit the last, empty block

    def _compute_file_line_length(self):
        """
        Inspect the file on disk and compute the binary length of the first non-header line.
        :return:
        """
        with gzip.open(self.bgzipped_fasta_filename, 'rb') as fasta_file_binary:
            first_line = fasta_file_binary.readline()
            assert first_line.startswith(b'>')
            file_line_length = len(fasta_file_binary.readline())
        return file_line_length

    def _compute_text_line_length(self):
        """
        Inspect the file on disk and compute the text length of the first non-header line.
        :return:
        """
        with gzip.open(self.bgzipped_fasta_filename, 'rt') as fasta_file_text:
            first_line = fasta_file_text.readline()
            assert first_line.startswith('>')
            text_line_length = len(fasta_file_text.readline().strip())
        return text_line_length

    def _get_contig_intervals_file_distance(self):
        """
        Determine the start and end locations of each contig sequence (not including headers) in the file.
        :return: A dictionary of tuples, keyed by contig name, storing (start, end) locations.
        """
        start_time = datetime.datetime.now()
        contig_intervals_file_distance = {}

        dbg_print('\tFinding contig locations ...')
        previous_sequence = None
        previous_start = 0
        # line_start = 0

        with gzip.open(self.bgzipped_fasta_filename, 'rb') as fasta_file:
            for line_num, line in enumerate(fasta_file):
                if line_num % 10000000 == 0:
                    dbg_print('\t\tprocessing line {:>10} ...'.format(line_num + 1))

                if line.startswith(b'>'):
                    sequence_name = re.split(WHITESPACE, line[1:].decode())[0]

                    if previous_sequence:
                        contig_intervals_file_distance[previous_sequence] = (
                            previous_start, fasta_file.tell() - len(line))

                    previous_start = fasta_file.tell()
                    previous_sequence = sequence_name

            contig_intervals_file_distance[previous_sequence] = (previous_start, fasta_file.tell() - len(line))

        dbg_print('\t\tFound {} sequences in {}.'.format(len(contig_intervals_file_distance),
                                                         datetime.datetime.now() - start_time))
        return contig_intervals_file_distance

    @staticmethod
    def _assign_blocks_to_contigs(contig_intervals_file_distance, block_interval_tree):
        """
        For each contig, create an interval tree that stores the sequence interval stored in each block
        (for all blocks that contain part of the contig), as well as the offset of the start of that
        block.

        :param contig_intervals_file_distance: A dictionary of intervals, keyed by contig name, storing the locations in the file spanned by each contig.
        :param block_interval_tree:  An interval tree storing the start and end locations in the uncompressed file spanned by each compressed block, as well as the offset of the block start.
        :return: Return a dictionary of such interval trees keyed by contig name.
        """
        start_time = datetime.datetime.now()
        dbg_print('\tAssigning compressed blocks to sequence contigs ...')

        sequence_blocks = {}

        for contig in sorted(contig_intervals_file_distance):

            if contig not in sequence_blocks:
                sequence_blocks[contig] = intervaltree.IntervalTree()

            for block_interval in block_interval_tree.search(*contig_intervals_file_distance[contig]):
                block_start_text_distance = block_interval.begin - contig_intervals_file_distance[contig][0]
                block_end_text_distance = block_interval.end - contig_intervals_file_distance[contig][0]
                sequence_blocks[contig].addi(block_start_text_distance, block_end_text_distance,
                                             block_interval.data)

        dbg_print('\t\tDone in {}'.format(datetime.datetime.now() - start_time))
        return sequence_blocks

    def _compute_contig_lengths(self, contig_intervals_file_distance):
        dbg_print('\tComputing contig lengths ...')
        self._contig_lengths = {}

        for contig in sorted(contig_intervals_file_distance):
            self._contig_lengths[contig] = self._file_distance_to_text_distance(
                offset_file_distance=contig_intervals_file_distance[contig][1],
                sequence_start_file_distance=contig_intervals_file_distance[contig][0]) - \
                                           self._file_distance_to_text_distance(
                                               offset_file_distance=contig_intervals_file_distance[contig][0],
                                               sequence_start_file_distance=contig_intervals_file_distance[contig][
                                                   0]) - 1
        dbg_print('\t\tDone.')

    def generate_index(self):
        """
        Generate an index for the FASTA file and store it in memory.

        :return:
        """
        overall_start_time = datetime.datetime.now()

        dbg_print('Generating index for sequence file {} ...'.format(self.bgzipped_fasta_filename))

        block_intervals_file_distance = self._get_blocks()

        start_time = datetime.datetime.now()
        dbg_print('\tGenerating interval tree from block spans ...')
        block_interval_tree = intervaltree.IntervalTree.from_tuples(block_intervals_file_distance)
        del block_intervals_file_distance
        dbg_print('\t\tDone in {}'.format(datetime.datetime.now() - start_time))

        self.line_length_file_distance = self._compute_file_line_length()
        dbg_print('\tEstimated file line size as {}'.format(self.line_length_file_distance))
        self.line_length_text_distance = self._compute_text_line_length()
        dbg_print('\tEstimated text line size as {}'.format(self.line_length_text_distance))

        contig_intervals_file_distance = self._get_contig_intervals_file_distance()

        self._index = self._assign_blocks_to_contigs(contig_intervals_file_distance=contig_intervals_file_distance,
                                                     block_interval_tree=block_interval_tree)
        self._compute_contig_lengths(contig_intervals_file_distance=contig_intervals_file_distance)

        dbg_print('\tDone generating index in {}.'.format(datetime.datetime.now() - overall_start_time))

    def save_index_to_text(self, index_filename=''):
        """
        Save the current index to a text file on disk.

        :param index_filename:
        :return:
        """
        start_time = datetime.datetime.now()
        dbg_print('Saving index to {} ...'.format(index_filename))
        with gzip.open(index_filename, 'wt') as index_file:
            index_file.write('{}\t{}\n'.format(self.line_length_file_distance, self.line_length_text_distance))
            for contig, intervals in sorted(self._index.items()):
                index_file.write('>{}\n'.format(contig))
                for interval in intervals:
                    index_file.write('{}\t{}\t{}\n'.format(interval.begin, interval.end, interval.data))
        dbg_print('\tDone in {}'.format(datetime.datetime.now() - start_time))

    def load_index_from_text(self, index_filename=''):
        """
        Load an index from a text file on disk.

        :param index_filename:
        :return:
        """
        start_time = datetime.datetime.now()
        dbg_print('Loading index from {} ...'.format(index_filename))

        # for whatever reason, it's faster to create an interval tree from a list of tuples than from adding intervals one at a time.
        index_tuples = {}

        with gzip.open(index_filename, 'rt') as index_file:
            line = index_file.readline()
            split_line = line.rstrip().split('\t')
            self.line_length_file_distance = int(split_line[0])
            self.line_length_text_distance = int(split_line[1])
            line = index_file.readline()

            contig = None
            while line is not '':
                if line.startswith('>'):
                    contig = line.rstrip()[1:]
                    index_tuples[contig] = []
                else:
                    index_tuples[contig].append([int(val) for val in line.rstrip().split('\t')])
                line = index_file.readline()

        self._index = {}
        for contig in index_tuples:
            self._index[contig] = intervaltree.IntervalTree.from_tuples(index_tuples[contig])

        dbg_print('\tDone in {}'.format(datetime.datetime.now() - start_time))

    def save_contig_lengths(self, contig_length_filename):
        """
        Saves the length of each contig to a tab-delimited 2-column table in :param:`contig_length_filename`
        :param contig_length_filename:
        :return:
        """
        dbg_print('Saving {} contig lengths to {} ...'.format(len(self._contig_lengths), contig_length_filename))
        with open(contig_length_filename, 'wt') as contig_length_file:
            for contig_name, contig_length in sorted(self._contig_lengths.items()):
                contig_length_file.write('{}\t{}\n'.format(contig_name, contig_length))
        dbg_print('\tDone.')

    def load_contig_lengths(self, contig_length_filename):
        """
        Retrieve the length of each contig from a tab-delimited 2-column table in :param:`contig_length_filename`
        :param contig_length_filename:
        :return:
        """
        dbg_print('Loading contig lengths from {} ...'.format(contig_length_filename))
        self._contig_lengths = {}
        with open(contig_length_filename, 'rt') as contig_length_file:
            for line in contig_length_file:
                split_line = line.split('\t')
                contig_name = split_line[0]
                contig_length = int(split_line[1])
                self._contig_lengths[contig_name] = contig_length
        dbg_print('Loaded {} contig lengths.'.format(len(self._contig_lengths)))

    def get_sequence(self, contig, start=0, end=0, strand=1):
        """
        Return the genomic DNA sequence spanning [start, end) on contig.

        :param contig: The name of the contig on which the start and end coordinates are located
        :param start: The start location of the sequence to be returned (this endpoint is included in the interval)
        :param end: The end location of the sequence to be returned (tis endpoint is not included in the interval)
        :param strand: The DNA strand of the sequence to be returned (-1 for negative strand, 1 for positive strand)
        :return: A string of DNA nucleotides of length end-start
        """
        if not contig in self._index:
            raise ContigNotFound(message='Contig {} not found'.format(contig),
                                 requested_contig=contig, valid_contigs=list(self._index.keys()))
        if end == 0:
            end = self.contig_lengths[contig]
            
        if start < 0:
            raise CoordinateOutOfBounds(message='Start coordinate below 0',
                                        problematic_coordinate=start,
                                        problem_with_start=True,
                                        coordinate_too_small=True,
                                        valid_coordinate_range=(0, self.contig_lengths[contig]),
                                        current_contig=contig)
        if start > self.contig_lengths[contig]:
            raise CoordinateOutOfBounds(message='Start coordinate past end of contig',
                                        problematic_coordinate=start,
                                        problem_with_start=True,
                                        coordinate_too_small=False,
                                        valid_coordinate_range=(0, self.contig_lengths[contig]),
                                        current_contig=contig)
        if end > self.contig_lengths[contig]:
            raise CoordinateOutOfBounds(message='End coordinate past end of contig',
                                        problematic_coordinate=end,
                                        problem_with_start=False,
                                        coordinate_too_small=False,
                                        valid_coordinate_range=(0, self.contig_lengths[contig]),
                                        current_contig=contig)
        if end < 0:
            raise CoordinateOutOfBounds(message='End coordinate below 0',
                                        problematic_coordinate=end,
                                        problem_with_start=False,
                                        coordinate_too_small=True,
                                        valid_coordinate_range=(0, self.contig_lengths[contig]),
                                        current_contig=contig)
        if start >= end:
            raise InvalidCoordinates(start=start, end=end)
            
        

        query_length = end - start
        start_pos_file_distance = self._text_distance_to_file_distance(start)

        start_block = sorted(self._index[contig].search(start_pos_file_distance))[0]
        start_block_offset = start_block.data
        dbg_print('Retrieving sequence for {} [{},{})'.format(contig, start, end))

        sequence_start_offset = start_pos_file_distance - start_block.begin

        retrieved_sequence = ''
        with bgzf.BgzfReader(self.bgzipped_fasta_filename, 'rt') as fasta_file:
            fasta_file.seek(bgzf.make_virtual_offset(start_block_offset, sequence_start_offset))
            while len(retrieved_sequence) < query_length:
                retrieved_sequence += fasta_file.readline().rstrip()
        trimmed_sequence = retrieved_sequence[:query_length]

        if strand == -1:
            return rev_complement(trimmed_sequence)
        else:
            return trimmed_sequence        


class Genome(object):
    """
    Serve up gene locations and sequences.
    """

    def __init__(self, genome_build,
                 sequence_file='',
                 feature_filename='',
                 feature_pickle_filename='',
                 sequence_chromosome_dialect='ucsc',
                 feature_chromosome_dialect='ensembl',
                 force_rebuild=False):
        
        if sequence_file:
            self.sequence_file = sequence_file
        else:
            self.sequence_file = BUILD_DATA[genome_build]['SEQUENCE_FILE']
        
        if feature_filename:
            self.feature_filename = feature_filename
        else:
            self.feature_filename = BUILD_DATA[genome_build]['FEATURE_FILENAME']
        
        if self.feature_filename.endswith('.gz'):
            self.feature_filename = self.feature_filename[:-3]
            
        if feature_pickle_filename:
            self.feature_pickle_filename = feature_pickle_filename
        else:
            self.feature_pickle_filename = BUILD_DATA[genome_build]['FEATURE_PICKLE_FILENAME']
                    
        #self.species = species
        self.build = genome_build
        self.sequence_chromosome_dialect = sequence_chromosome_dialect
        self.feature_chromosome_dialect = feature_chromosome_dialect

        # Initialize sequence object
        self.genome_sequence = GenomeSequence(self.sequence_file)

        # Initialize features either from pre-generated data or de-novo from a G*F file
        if not force_rebuild:
            try:
                feature_pickle_file = find_file_gzipped(self.feature_pickle_filename, 'rb')
                if feature_pickle_file:
                    start_time = datetime.datetime.now()
                    self.features, self.feature_to_id = pickle.load(feature_pickle_file)
                    feature_pickle_file.close()
                    dbg_print('Loaded genome features from {} in {}.'.format(self.feature_pickle_filename,
                                                                             datetime.datetime.now() - start_time))
                else:
                    dbg_print('Pre-made feature file not found; Will generate now ...')
                    force_rebuild = True
            except (ImportError, IOError, OSError, pickle.UnpicklingError, AttributeError, EOFError, ValueError) as e:
                dbg_print('Failed to load cached features: {}'.format(e))
                force_rebuild = True

        if force_rebuild:
            self._populate_features()
            # self._populate_contig_lengths()

    @property
    def contig_names(self):
        """
        Return a list of all the valid sequence contigs in this genome.
        """
        return list(self.genome_sequence.contig_lengths.keys())

    @property
    def contig_lengths(self):
        """
        Return a dictionary of sequence contigs and their lengths.
        """
        return self.genome_sequence.contig_lengths

    @property
    def size(self):
        """
        Size of the genome, in base pairs
        """
        return sum(self.contig_lengths.values())
                
    def random_contigs(self, num_contigs):
        """
        Return a list of :param:`num_contigs` contigs chosen randomly (with replacement) from a multinomial distribution of contigs weighted by contig
        length (i.e. the probability of a contig being chosen is its proportion of the total genome (or at least the total of all listed contigs) 
        """
        contig_probabilities = numpy.array(list(self.contig_lengths.values()), dtype=numpy.float)/sum(self.contig_lengths.values())
        return numpy.random.choice(list(self.contig_lengths.keys()), size=num_contigs, p=contig_probabilities)
        
    def trim_contigs(self, keep_sex=True):
        self.genome_sequence.trim_contigs(keep_sex=keep_sex)

    def _populate_features(self):
        """
        Generate the internal data structures based on information in the G*F file and the contigs' lengths.
        """
        start_time = datetime.datetime.now()
        dbg_print('Generating gene info and translation data from GFF file {} ...'.format(self.feature_filename))

        feature_file = find_file_gzipped(self.feature_filename, 'rt')
        if feature_file is None:
            raise Exception(
                'G*F file not found! Looked for {} and {}'.format(self.feature_filename,
                                                                  self.feature_filename + '.gz'))
        # Generate from G*F
        if self.feature_filename.endswith('gff3'):
            features, self.feature_to_id = parse_gff3(feature_file)
        elif self.feature_filename.endswith('gtf'):
            features, self.feature_to_id = parse_gtf(feature_file)
        else:
            raise Exception('Invalid GFF filename. Must end in .gff3 or .gtf')
        feature_file.close()

        # Get features
        self.features = IntervalDict(features)

        # Pickle for future use
        with gzip.open(self.feature_pickle_filename + '.gz', 'wb') as feature_pickle_file:
            pickle.dump((self.features, self.feature_to_id), feature_pickle_file, protocol=-1)

        dbg_print('{} genes by Ensembl ID, {} gene symbols in {}'.format(len(self.features), len(self.feature_to_id),
                                                                         datetime.datetime.now() - start_time))

    def get_gene_by_ensembl_id(self, ensembl_id):
        """
        Return a dictionary of information fields about the gene specified by the given <ensembl_id>.

        :param ensembl_id:
        :return:
        """
        return self.features[ensembl_id]

    def get_gene_by_name(self, gene_name):
        """
        Return a dictionary of information fields about the gene specified by the <gene_name>.
        Return None if the <gene_name> has no Ensembl ID or if the Ensembl ID is not found.

        :param gene_name:
        :return:
        """
        # Look up this <gene_name> in the gene-name-to-Ensembl-ID dictionary
        if gene_name in self.feature_to_id:
            # If found, then get this <gene_name>'s Ensembl ID
            ensembl_id = self.feature_to_id[gene_name]

            # Then look up this Ensembl ID within the list of Ensembl IDs stored
            if ensembl_id in self.features:
                # Return found feature information corresponding to this Ensembl ID
                return self.features[ensembl_id]
        raise GeneNotFound(gene_name)

    def get_genes_by_location(self, contig, start=0, end=0, strand=0, strict=False):
        """
        Return an ordered  dictionary of genes overlapping the specified region.
        Currently ignores <strand> parameter, returning genes on both strands.

        :param contig:
        :param start:
        :param end:
        :param strand:
        :param strict:
        :return:
        """
        if contig not in self.contig_names:
            raise ContigNotFound(contig, self.contig_names)
            # if the requested contig is in self.contig names, it's valid, but if there are no genes there it
            # may not exist in the features object.
        if contig in self.features.contig_names:
            return self.features.overlapping(contig=contig, start=start, end=end, strict=strict)
        else:
            return []

    def get_dna_sequence(self, contig, start=0, end=0, strand=1):
        """
        Return the sequence of the specified genomic region.

        :param contig:
        :param start:
        :param end:
        :param strand:
        :return:
        """
        if contig not in self.contig_names:
            raise ContigNotFound(contig, self.contig_names)
        return self.genome_sequence.get_sequence(contig=contig, start=start, end=end, strand=strand)

    def get_dna_sequence_by_name(self, gene_name):
        """
        Return the genomic sequence of the specified <gene_name>.

        :param gene_name:
        :return:
        """
        gene_info = self.get_gene_by_name(gene_name)
        
        return self.genome_sequence.get_sequence(contig=gene_info['contig'], start=gene_info['start'], end=gene_info['end'])
        
    def get_promoters(self, promoter_upstream=PROMOTER_UPSTREAM, promoter_downstream=PROMOTER_DOWNSTREAM, key_by='ensembl'):
        """
        Returns an IntervalDict containing the genomic loci of all promoters in the genome, named by gene,
        as defined  by the region :param:`promoter_upstream` bp upstream of the TSS to :param:`promoter_downstream` bp
        downstream of the TSS. The promote region will be truncated if it extends past the boundaries of 
        the chromosome. Currently not truncated if it intersects another genome feature (may be implemented
        later).
        """
        
        promoters = IntervalDict()
        assert key_by in ('ensembl', 'hugo'), 'parameter key_by must be one of: ensembl, hugo'

        for gene_name, gene_info in list(self.features.items()):
            if key_by == 'hugo':
                gene_name = gene_info['gene_name']
                
            contig = gene_info['contig']
            if contig in self.contig_lengths:
                if gene_info['strand'] == 1:        
                    promoter_start = max(0, gene_info['start'] - promoter_upstream)
                    promoter_end = min(self.contig_lengths[contig], gene_info['start'] + promoter_downstream)
                else:
                    promoter_start = max(0, gene_info['end'] - promoter_downstream)
                    promoter_end = min(self.contig_lengths[contig], gene_info['end'] + promoter_upstream)

                promoters[gene_name] = {'contig':contig, 'start':promoter_start, 'end':promoter_end, 'strand':gene_info['strand']}
        
        return promoters
        
    def compute_nucleotide_frequencies(self):
        """
        Computes the frequency of each nucleotide in the genome and returns it as a dictionary keyed by nucleotide
        :return:
        """
        
        return motiftools.compute_background_distribution(self.whole_genome, normalize=True)        
                
    def get_whole_genome_sequence(self):
        """
        Returns the sequence of the entire genome, concatenated in alpha
        contig order, as a single string.
        """
        return ''.join((self.get_dna_sequence(contig=chrom) for chrom in sorted(self.contig_names)))
        
    def random_regions(self, num, region_length, stranded=True, random_seed=None):
        """
        Returns a list of (contig, start, end) tuples for :param:`num` genomic regions sampled
        from a uniform distribution over all base pairs.
        """
        numpy.random.seed(random_seed)
        
        contig_weights = {contig:self.contig_lengths[contig]/self.size for contig in self.contig_lengths}
        sorted_contigs = sorted(self.contig_names)
        contig_p = numpy.array([contig_weights[contig] for contig in sorted_contigs])
        
        regions=[]
        
        for i in range(num):
            random_contig = numpy.random.choice(sorted_contigs, p=contig_p)
            start_pos = numpy.random.randint(0, self.contig_lengths[random_contig] - region_length)
            end_pos = start_pos + region_length
            
            if stranded:
                random_strand = numpy.random.choice(('-', '+'))
                regions.append((random_contig, start_pos, end_pos, random_strand))
            else:
                regions.append((random_contig, start_pos, end_pos))
        return regions
        
    def get_all_sequences(self):
        """
        Returns the entire genome as a dictionary of strings keyed by contig name.
        """
        return {contig:self.get_dna_sequence(contig) for contig in self.contig_names}


class Variants(object):
    """
    Serve up variants from a tabix-indexed VCF file.
    """
    # field mappings for various flavors of VCF
    FREE_BAYES = {'primary_key': {'rs_id': (2, str)},
                    'core_fields':
                      {'contig': (0, str),
                       'start': (1, int),
                       'ref': (3, str),
                       'alt': (4, str),
                       'qual': (5, float)
                       },
                  'info_position': 7,
                  'secondary_field_keys': 8,
                  'secondary_field_values': 9,
                  }

    class Variant(tables.IsDescription):
        rs_id = tables.StringCol(16)
        is_snp = tables.BoolCol()
        contig = tables.StringCol(64)
        start = tables.Int32Col()
        end = tables.Int32Col()
        ref = tables.StringCol(256)
        alt = tables.StringCol(256)
        qual = tables.Float32Col()
        affected_area = tables.StringCol(64)
        putative_impact = tables.StringCol(8)
        affected_gene = tables.StringCol(16)
        pathogenicity = tables.Int32Col()
        GT = tables.StringCol(16)
        AD = tables.StringCol(16)
        DP = tables.StringCol(16)
        GQ = tables.StringCol(16)
        PL = tables.StringCol(16)

    def __init__(self, vcf_filename=VARIANT_FILENAME, vcf_field_model=FREE_BAYES,
                 variant_table_filename=VARIANT_PYTABLE_FILENAME,
                 variant_rs_id_index_filename=VARIANT_RS_ID_INDEX_FILENAME,
                 force_rebuild=False, chromosome_dialect=CHROMOSOME_DIALECT):
        """
        Create an object used to interface with tables of client Variant information on disk.

        :param vcf_filename:
        :param vcf_field_model:
        :param variant_table_filename:
        :param variant_rs_id_index_filename:
        :param force_rebuild:
        :param chromosome_dialect:
        """
        self.vcf_filename = vcf_filename
        self.vcf_field_model = vcf_field_model
        self.variant_rs_id_index_filename = variant_rs_id_index_filename
        self.chromosome_dialect = chromosome_dialect

        self.variant_file = None
        self.rs_id_index = {}

        # Try opening the cached data file:
        start_time = datetime.datetime.now()
        if not force_rebuild:
            try:
                dbg_print('Opening Variant table file {}.'.format(variant_table_filename))
                self.variant_file = tables.open_file(filename=variant_table_filename, mode='r')
                dbg_print('\tDone in {}'.format(datetime.datetime.now() - start_time))
                self._load_rs_id_index(self.variant_rs_id_index_filename)
            except (OSError, IOError, tables.HDF5ExtError):
                dbg_print('\tFailed!')
                force_rebuild = True
                if self.variant_file:
                    self.variant_file.close()

        # Force extraction of information from VCF and generating new table
        if force_rebuild:
            self._populate_from_vcf(vcf_filename, variant_table_filename)
            self._save_rs_id_index(self.variant_rs_id_index_filename)
            # re-open the table file in read-only mode for later use.
            self.variant_file = tables.open_file(filename=variant_table_filename, mode='r')

        self.variant_group = self.variant_file.get_node('/variants')

    def __del__(self):
        """
        Destructor. Makes sure that the HDF5 variant file is explicitly closed.
        :return:
        """
        if self.variant_file:
            self.variant_file.close()

    def _save_rs_id_index(self, variant_rs_id_index_filename):
        """
        Saves the index mapping rs_ids to contigs to a pickle contained in :param:`variant_rs_id_index_filename`
        :param variant_rs_id_index_filename:
        :return:
        """
        start_time = datetime.datetime.now()
        dbg_print('Saving rs_id index to {}...'.format(variant_rs_id_index_filename))
        with gzip.open(variant_rs_id_index_filename, 'wb') as index_file:
            pickle.dump(self.rs_id_index, index_file, protocol=-1, fix_imports=True)
        dbg_print('\tDone in {}'.format(datetime.datetime.now() - start_time))

    def _load_rs_id_index(self, variant_rs_id_index_filename):
        """
        Load the index mapping rs_ids to contigs into memory from :param:`variant_rs_id_index_filename`

        :param variant_rs_id_index_filename:
        :return:
        """
        start_time = datetime.datetime.now()
        dbg_print('Loading rs_id index from {}...'.format(variant_rs_id_index_filename))
        with gzip.open(variant_rs_id_index_filename, 'rb') as index_file:
            self.rs_id_index = pickle.load(index_file, fix_imports=True)
        dbg_print('\tDone in {}'.format(datetime.datetime.now() - start_time))

    def _insert_vcf_row(self, variant_tuple, variant_cursor):
        """
        Parse a tuple of VCF 4.2 entries and insert them into the current row specified by <variant_cursor>

        Annotation of CLNSIG field: "Variant Clinical Significance, 0 - Uncertain significance, 1 - not provided, 2 - Benign, 3 - Likely benign, 4 - Likely pathogenic, 5 - Pathogenic, 6 - drug response, 7 - histocompatibility, 255 - other"

        :param variant_tuple:
        :param variant_cursor:
        :return:
        """
        # Split up multiple entries in rs_id field (if present)
        primary_key_field = list(self.vcf_field_model['primary_key'].keys())[0]
        primary_key_pos, primary_key_parse_func = self.vcf_field_model['primary_key'][primary_key_field]

        primary_keys = primary_key_parse_func(variant_tuple[primary_key_pos]).split(';')

        if len(primary_keys) > 1:
            dbg_print('Got multiple ids for same variant: {}'.format(', '.join(primary_keys)))

        for primary_key in primary_keys:
            # Assign the primary key to this variant. Note that re-doing the parsing for each of the ids in a multi-id
            #  variant, as we do below, is not the most efficient way of handling this situation. But since this is expected
            #  to be rare, we don't optimize yet.
            variant_cursor[primary_key_field] = primary_key

            # get core fields
            for field_name, (field_position, parse_func) in list(self.vcf_field_model['core_fields'].items()):
                variant_cursor[field_name] = parse_func(variant_tuple[field_position])

            variant_cursor['contig'] = convert_chroms(variant_cursor['contig'].decode(), self.chromosome_dialect)

            variant_cursor['start'] -= 1  # convert 1-based sequence index to 0-based
            # end position is with respect to reference sequence
            variant_cursor['end'] = variant_cursor['start'] + len(variant_cursor['ref'])
            # get info fields
            split_info = variant_tuple[self.vcf_field_model['info_position']].split(';')

            for field_atom in split_info:
                try:
                    field_key, field_value = field_atom.split('=')
                except ValueError:
                    pass
                else:
                    # Parse the annotation field
                    if field_key == 'ANN':
                        annotations = field_value.split('|')
                        variant_cursor['affected_area'] = annotations[1]
                        variant_cursor['putative_impact'] = annotations[2]
                        variant_cursor['affected_gene'] = annotations[3]

                    if field_key == 'CLNSIG':
                        clinsig_values = [int(v) for v in field_value if field_value in {'2', '3', '4', '5'}]
                        if len(clinsig_values) > 0:
                            variant_cursor['pathogenicity'] = numpy.mean(clinsig_values)

                    # Look at the comma-separated elements of the alt field and the ref field. If any
                    # of them are longer than 1 nucleotide, classify this variant as an indel,
                    # otherwise it is a SNP.
                    variant_cursor['is_snp'] = True
                    for allele in variant_cursor['alt'].decode().split(',') + [variant_cursor['ref']]:
                        if len(allele) > 1:
                            variant_cursor['is_snp'] = False

            # Process "secondary" fields that have field names in column 8 and values in column 9, all
            # colon-delimited.
            # TODO: fails on clinical sample
            try:
                for key, value in zip(variant_tuple[self.vcf_field_model['secondary_field_keys']].split(':'),
                                      variant_tuple[self.vcf_field_model['secondary_field_values']].split(':')):
                    variant_cursor[key] = value
            except IndexError:
                dbg_print('Error in FORMAT and/or SAMPLE column')

            # update map of rs_id to contigs
            self.rs_id_index[variant_cursor['rs_id'].decode()] = variant_cursor['contig'].decode()

            variant_cursor.append()

    def _populate_from_vcf(self, vcf_filename, variant_table_filename, minimum_quality=0):
        """
        Generate internal data structures from VCF file and cache them
        to disk for future reference. Only store variants having quality scores greater
        than <minimum_quality>
        """
        start_time = datetime.datetime.now()
        dbg_print('Parsing VCF file and building variant table ...')

        # open the vcf file and iterate over it
        with gzip.open(vcf_filename, 'rt') as vcf_file:
            # skip past comments and header
            line = vcf_file.readline()
            while line.startswith('#'):
                # remember this position so we can seek back to it
                data_start_pos = vcf_file.tell()
                line = vcf_file.readline()

            # count rows
            dbg_print('Pass 1 of 2: Counting number of rows in each contig ...')
            precount_start_time = datetime.datetime.now()

            rows_per_contig = collections.defaultdict(lambda: 0)
            line = vcf_file.readline()
            while line != '':
                rows_per_contig[convert_chromosome(line.split('\t')[self.vcf_field_model['core_fields']['contig'][0]],
                                                   self.chromosome_dialect)] += 1
                line = vcf_file.readline()

            dbg_print('\tDone in {}'.format(datetime.datetime.now() - precount_start_time))
            vcf_file.seek(data_start_pos)

            # initialize table file
            with tables.open_file(filename=variant_table_filename, mode='w', title='Client variant information',
                                  filters=tables.Filters(complevel=VARIANT_PYTABLE_COMPRESSION_LEVEL,
                                                         complib=VARIANT_PYTABLE_COMPRESSOR)) as h5file:
                # initialize group
                self.variant_group = h5file.create_group('/', 'variants', 'Client sequence variants')
                # create a dictionary of cursors (pointer to the currently active row)
                variant_cursors = {}

                # parse the tuples in each row and stick them into our tables
                dbg_print('Pass 2 of 2: Populating variant table from VCF contents...')
                for row_num, vcf_row in enumerate(vcf_file):
                    if row_num % 1000000 == 0:
                        dbg_print('\tProcessing VCF row {} ...'.format(row_num + 1))
                    if vcf_row is not '':
                        split_row = vcf_row.rstrip().split('\t')
                        contig = convert_chromosome(split_row[0], self.chromosome_dialect)
                        if contig not in variant_cursors:
                            dbg_print('\tCreating variant table for contig {} ...'.format(contig))
                            new_table = h5file.create_table(where=self.variant_group,
                                                            name='contig_{}_variants'.format(contig),
                                                            description=self.Variant,
                                                            title='Variants for contig {}'.format(contig),
                                                            expectedrows=rows_per_contig[contig])

                            variant_cursors[contig] = new_table.row

                        self._insert_vcf_row(split_row, variant_cursors[contig])

                for contig in variant_cursors:
                    variant_table = self.variant_group._f_get_child('contig_{}_variants'.format(contig))
                    variant_table.flush()
                    # create index
                    for col_name in sorted((
                            'contig', 'start', 'end', 'pathogenicity', 'putative_impact', 'qual', 'rs_id')):
                        dbg_print('\tGenerating index for column {} in contig {}'.format(col_name, contig))
                        variant_table.cols._f_col(col_name).create_csindex(tmp_dir='/tmp')

        dbg_print('\tDone in {}'.format(datetime.datetime.now() - start_time))

    @staticmethod
    def _tuple_to_dict(variant_tuple, col_names):
        """
        Converts a tuple of variant information as output from a PyTables query, and returns a dictionary
        of field-value pairs. Bytes will be converted to strings as appropriate.
        :param variant_tuple:
        :param col_names:
        :return:
        """
        variant_dict = {}
        for key, value in zip(col_names, variant_tuple):
            try:
                variant_dict[key] = value.decode()
            except AttributeError:
                variant_dict[key] = value
        variant_dict['client_alleles'] = determine_client_alleles(gt_field=variant_dict['GT'],
                                                                  ref=variant_dict['ref'],
                                                                  alt=variant_dict['alt'])
        return variant_dict

    def get_variant_by_rs_id(self, rs_id, allow_snps=True, allow_indels=False):
        """
        Return a dictionary of variant attributes for the variant matching <rs_id>.
        If <rs_id> is not found, return None.
        """
        if rs_id in self.rs_id_index:
            contig = self.rs_id_index[rs_id]
            query_string = '(rs_id == {})'.format(rs_id.encode())

            if allow_snps and allow_indels:
                pass
            elif allow_snps:
                query_string += ' & (is_snp == True)'
            else:
                query_string += ' & (is_snp == False)'

            dbg_print('Query: {}'.format(query_string))
            table = self.variant_group._f_get_child('contig_{}_variants'.format(contig))
            query_results = table.read_where(query_string)

            if len(query_results) > 0:
                return self._tuple_to_dict(query_results[0], table.colnames)

        return None

    def get_variants_by_location(self, contig, start=0, end=0, minimum_quality=0, allow_snps=True, allow_indels=False,
                                 minimum_pathogenicity=0, include_putative_impacts=(), exclude_putative_impacts=(),
                                 convert_to_dict=False):
        """
        Given a genomic region specified by <contig>, <start>, <end>,
        return all variants overlapping that region.

        :param contig:
        :param start:
        :param end:
        :param minimum_quality:
        :param allow_snps: Whether or not SNPs (variants with either alt or ref fields equal to one nucleotide) should be returned.
        :param allow_indels: Whether or not indels (variants with either alt or ref fields greater than one nucleotide) should be returned.
        :param minimum_pathogenicity: An integer. If set, any variants below this pathogenicity level will be excluded.
        :param include_putative_impacts: An iterable. If set, only variants with these putative impact classifications will be returned
        :param exclude_putative_impacts: An iterable. If set, variants with these putative impact classifications will not be returned
        :param convert_to_dict: If True, return a list of dictionaries of field-value pairs,
         otherwise return a tuple consisting of a list of tuples, and a dictionary mapping field
         names to tuple indices.
        :return:
        """
        start_time = datetime.datetime.now()
        dbg_print(
            'Finding all variants of in contig {} ({},{}) with quality > {}, SNPS: {}, Indels: {}...'.format(contig,
                                                                                                             start,
                                                                                                             end,
                                                                                                             minimum_quality,
                                                                                                             allow_snps,
                                                                                                             allow_indels))
        try:
            table = self.variant_group._f_get_child('contig_{}_variants'.format(contig))
        except tables.exceptions.NoSuchNodeError:
            # We have no variant info for this contig. Either because it's not a valid contig or there were no variants
            # there.
            if convert_to_dict:
                return []
            else:
                return [], {}

        if start > 0 or end > 0:
            query_string = (
                '(contig == {}) & (start >= {}) & (end <= {}) & (qual > {})'.format(contig.encode(), start, end,
                                                                                    minimum_quality))
        else:
            query_string = ('(contig == {}) & (qual > {})'.format(contig.encode(), minimum_quality))

        if allow_snps and allow_indels:
            pass
        elif allow_snps:
            query_string += ' & (is_snp == True)'
        else:
            query_string += ' & (is_snp == False)'

        include_putative_impacts = set(include_putative_impacts)
        exclude_putative_impacts = set(exclude_putative_impacts)
        include_putative_impacts.difference_update(exclude_putative_impacts)

        if include_putative_impacts:
            query_string += ' & ({})'.format(' | '.join(
                ['(putative_impact == {})'.format(included_impact.encode()) for included_impact in
                 include_putative_impacts]))

        if exclude_putative_impacts:
            query_string += ' & ({})'.format(' & '.join(
                ['(putative_impact != {})'.format(excluded_impact.encode()) for excluded_impact in
                 exclude_putative_impacts]))

        if minimum_pathogenicity:
            query_string += ' & (pathogenicity >= {}'.format(minimum_pathogenicity)

        dbg_print('Query: {}'.format(query_string))

        query_results = table.read_where(query_string)

        dbg_print('\tFound {} variants in {}'.format(len(query_results), datetime.datetime.now() - start_time))

        if convert_to_dict:
            start_time = datetime.datetime.now()
            dbg_print('Converting variants to dictionaries...')
            query_results = [self._tuple_to_dict(var, table.colnames) for var in query_results]
            dbg_print('\tDone in {}'.format(datetime.datetime.now() - start_time))
            return query_results
        else:
            field_mapping = dict([t[::-1] for t in enumerate(table.colnames)])
            return query_results, field_mapping

    def get_variant_columns_by_location(self, contig, start=0, end=0, minimum_quality=0, allow_snps=True,
                                        allow_indels=False,
                                        minimum_pathogenicity=0, include_putative_impacts=(),
                                        exclude_putative_impacts=(),
                                        fields=(
                                                'start', 'end', 'putative_impact', 'pathogenicity', 'ref', 'alt',
                                                'GT')):
        """
        Similar to .get_variants_by_location except that instead of returning an array of structured arrays
        or a list of dictionaries, this method returns a dictionary of arrays, one for each column in the
        result. Iterating over these arrays is much faster than over the row iterator returned by standard
        query methods.

        :param contig:
        :param start:
        :param end:
        :param minimum_quality:
        :param allow_snps:
        :param allow_indels:
        :param minimum_pathogenicity:
        :param include_putative_impacts:
        :param exclude_putative_impacts:
        :param fields: Which fields will be included as columns in the result
        :return:
        """
        start_time = datetime.datetime.now()
        dbg_print(
            'Finding all variants of in contig {} ({},{}) with quality > {}, SNPS: {}, Indels: {}...'.format(contig,
                                                                                                             start,
                                                                                                             end,
                                                                                                             minimum_quality,
                                                                                                             allow_snps,
                                                                                                             allow_indels))

        dbg_print('Returning arrays for fields {}.'.format(', '.join(fields)))


        try:
            table = self.variant_group._f_get_child('contig_{}_variants'.format(contig))
        except tables.exceptions.NoSuchNodeError:
            # We have no variant info for this contig. Either because it's not a valid contig or there were no variants
            # there.
            return dict([(field, []) for field in fields])

        if start > 0 or end > 0:
            query_string = (
                '(contig == {}) & (start >= {}) & (end <= {}) & (qual > {})'.format(contig.encode(), start, end,
                                                                                    minimum_quality))
        else:
            query_string = ('(contig == {}) & (qual > {})'.format(contig.encode(), minimum_quality))

        if allow_snps and allow_indels:
            pass
        elif allow_snps:
            query_string += ' & (is_snp == True)'
        else:
            query_string += ' & (is_snp == False)'

        include_putative_impacts = set(include_putative_impacts)
        exclude_putative_impacts = set(exclude_putative_impacts)
        include_putative_impacts.difference_update(exclude_putative_impacts)

        if include_putative_impacts:
            query_string += ' & ({})'.format(' | '.join(
                ['(putative_impact == {})'.format(included_impact.encode()) for included_impact in
                 include_putative_impacts]))

        if exclude_putative_impacts:
            query_string += ' & ({})'.format(' & '.join(
                ['(putative_impact != {})'.format(excluded_impact.encode()) for excluded_impact in
                 exclude_putative_impacts]))

        if minimum_pathogenicity:
            query_string += ' & (pathogenicity >= {}'.format(minimum_pathogenicity)

        dbg_print('Query: {}'.format(query_string))

        row_coordinates = [r.nrow for r in table.where(query_string)]
        query_results = {}
        for field in fields:
            query_results[field] = table.read_coordinates(row_coordinates, field=field)

        dbg_print(
            '\tFound {} variants in {}'.format(len(query_results[list(query_results.keys())[0]]),
                                               datetime.datetime.now() - start_time))
        return query_results


class DescribedVariant(tables.IsDescription):
    rs_id = tables.StringCol(11)
    clinvar_allele = tables.StringCol(55)
    clin_sig = tables.StringCol(39)
    phenotype = tables.StringCol(419)
    description = tables.StringCol(12390)


class KnownVariant(tables.IsDescription):
    rs_id = tables.StringCol(11)
    contig = tables.StringCol(2)
    start = tables.Int32Col()
    ref = tables.StringCol(250)
    alt = tables.StringCol(320)
    gene = tables.StringCol(178)
    af = tables.StringCol(77)