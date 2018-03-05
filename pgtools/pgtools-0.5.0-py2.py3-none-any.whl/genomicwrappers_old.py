import gzip
import os
import re
from subprocess import call  # ToDo: remove once Python 3.5 available in Anaconda

run = call
import collections
import csv
import datetime
import numpy
import intervaltree
#import intervaloverlaps
import pickle
import vcf
import pysam
import pandas
from pgtools import toolbox, intervaloverlaps

FASTA_FOLDER = ''
FASTA_FNAME_PREFIX = ''
FASTA_FNAME_SUFFIX = ''

REPORTING_INTERVAL = 10000

GFF_FNAME = ''

DEFAULT_CHROMOSOME_DIALECT = 'ensembl'
GZIPPED_FASTA = False
GFF_GENE_SOURCES = ['ensembl_havana']
GFF_GENE_IDENTIFIERS = ['gene']

GENE_INFO_PICKLE_FNAME = ''

CODON_TABLE = {'GUC': 'V', 'ACC': 'T', 'GUA': 'V', 'GUG': 'V', 'GUU': 'V', 'AAC': 'N', 'CCU': 'P', 'UGG': 'W',
               'AGC': 'S', 'AUC': 'I', 'CAU': 'H', 'AAU': 'N', 'AGU': 'S', 'ACU': 'T', 'CAC': 'H', 'ACG': 'T',
               'CCG': 'P', 'CCA': 'P', 'ACA': 'T', 'CCC': 'P', 'GGU': 'G', 'UCU': 'S', 'GCG': 'A', 'UGC': 'C',
               'CAG': 'Q', 'GAU': 'D', 'UAU': 'Y', 'CGG': 'R', 'UCG': 'S', 'AGG': 'R', 'GGG': 'G', 'UCC': 'S',
               'UCA': 'S', 'GAG': 'E', 'GGA': 'G', 'UAC': 'Y', 'GAC': 'D', 'GAA': 'E', 'AUA': 'I', 'GCA': 'A',
               'CUU': 'L', 'GGC': 'G', 'AUG': 'M', 'CUG': 'L', 'CUC': 'L', 'AGA': 'R', 'CUA': 'L', 'GCC': 'A',
               'AAA': 'K', 'AAG': 'K', 'CAA': 'Q', 'UUU': 'F', 'CGU': 'R', 'CGA': 'R', 'GCU': 'A', 'UGU': 'C',
               'AUU': 'I', 'UUG': 'L', 'UUA': 'L', 'CGC': 'R', 'UUC': 'F', 'UAA': 'X', 'UAG': 'X', 'UGA': 'X'}

ALPHANUMERIC = [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]

WHITESPACE = re.compile(r'\s*')

STRAND_TO_INT = {'+': 1, '-': -1}

GENOMIC_DATA_BASEPATH = toolbox.home_path('oasis_local/reference_genomes', )

SPECIES_DATA = {'human': {'ensembl_build': 'GRCh38.83',
                          'ensembl_name': 'Homo_sapiens',
                          'ucsc_build': 'hg38',
                          },
                'mouse': {'ensembl_build': 'GRCm38.83',
                          'ensembl_name': 'Mus_musculus',
                          'ucsc_build': 'mm10'
                          }
                }


def lightweight_gff_parser(gff_fname, sources=[], identifiers=[]):
    """
    Simple GFF parser that returns a list of dictionaries of items matching the selected sources and identifiers

    :param gff_fname:
    :param sources:
    :param identifiers:
    :return:
    """
    sources = set(sources)
    identifiers = set(identifiers)

    items = []

    with open(gff_fname, 'rt') as gff_file:
        for line in gff_file:
            if line[0] != '#':  # not a header ine
                split_line = line.split('\t')
                source, identifier = split_line[1], split_line[2]
                if source in sources and identifier in identifiers:
                    # if we have a match, process the rest of the line
                    chrom = split_line[0]
                    start = int(split_line[3])
                    end = int(split_line[4])
                    strand = split_line[6]
                    fields = dict((field_value_pair.split('=') for field_value_pair in split_line[8].split(';')))
                    items.append({'chrom': chrom, 'start': start, 'end': end, 'strand': strand, 'fields': fields})
    return items


def gff_to_gene_dict(gff_file, sources=GFF_GENE_SOURCES, identifiers=GFF_GENE_IDENTIFIERS):
    """
    Simple GFF parser that returns a dictionary of genes keyed by Ensembl ID, as well as a translation dictionary
    mapping gene names to Ensembl IDs.
    """
    sources = set(sources)
    identifiers = set(identifiers)

    gene_dict, gene_name_to_ensembl = {}, {}

    for line_num, line in enumerate(gff_file):
        if line[0] != '#':  # not a header ine
            split_line = line.split('\t')
            if len(split_line) < 7:
                print((line_num, split_line))
            source, identifier = split_line[1], split_line[2]
            if source in sources and identifier in identifiers:
                # if we have a match, process the rest of the line

                chrom = split_line[0]
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

                assert ensembl_id not in gene_dict  # make sure no duplicate ensembl IDs
                gene_dict[ensembl_id] = {'chrom': chrom, 'start': start, 'end': end, 'strand': strand,
                                         'version': version, 'gene_name': gene_name, 'ensembl_id': ensembl_id}

                if gene_name not in gene_name_to_ensembl or version > gene_dict[ensembl_id]['version']:
                    gene_name_to_ensembl[gene_name] = ensembl_id

    return gene_dict, gene_name_to_ensembl


def get_chrom_length_dict(genome_table_fname, dest_chromosome_dialect=DEFAULT_CHROMOSOME_DIALECT):
    print(('Getting chromosome lengths from {} and translating names to dialect {}'.format(genome_table_fname,
                                                                                           dest_chromosome_dialect)))
    with open(genome_table_fname, 'rt') as gt_file:
        length_dict = {}
        for line in gt_file:
            # print line
            split_line = re.split(r'\s', line.strip())
            if len(split_line) > 1:
                # print split_line[0], toolbox.parse_chromosome_ID(split_line[0])
                length_dict[toolbox.convert_chroms(split_line[0], dest=dest_chromosome_dialect)] = int(split_line[1])
                # length_dict[split_line[0].strip()] = int(split_line[1])
    return length_dict


def compute_fasta_offset(sequence_location, header_size, line_size, cr_lf_size=1):
    """
    Given a location on a FASTA sequence (assuming one sequence per file),
    the length of the header line and a line length (including CR/LF),
    (assumes the line size is constant throughout the file),
    return the file location of the specified sequence location

    :param sequence_location:
    :param header_size:
    :param line_size:
    :param cr_lf_size:
    :return:
    """
    num_lines = int(sequence_location / (line_size - cr_lf_size))
    line_offset = sequence_location % (line_size - cr_lf_size)
    return num_lines * line_size + line_offset + header_size


def convert_chroms(chrom_string, dest='ucsc'):
    """
    Refactored to auto-detect source (<source> parameter will be ignored).
    :param chrom_string:
    :param dest:
    :return:
    """
    # try:
    #     chrom_string = str(romannumerals.roman_to_int(chrom_string))
    # except ValueError:
    #     pass

    if dest == 'ensembl':
        if chrom_string == 'chrM':
            return 'dmel_mitochonrdion_genome'
        elif chrom_string[:3].lower() == 'chr':
            return chrom_string[3:]
        else:
            return chrom_string
    elif dest == 'ucsc':
        if chrom_string == 'dmel_mitochondrion_genome':
            return 'chrM'
        elif chrom_string[:3].lower() == 'chr':
            return chrom_string
        else:
            return 'chr{}'.format(chrom_string)
    # elif dest == 'yeast':
    #     if chrom_string[:3].lower() == 'chr':
    #         chrom_string = chrom_string[3:]
    #     try:
    #         return romannumerals.int_to_roman(int(chrom_string))
    #     except ValueError:
    #         return chrom_string

    else:
        raise ValueError('Unknown destination {}'.format(dest))


def find_file_gzipped(base_filename, mode='r'):
    """
    Convenience function that looks first for a gzipped version of a file, then a plaintext
    version, and returns a file handle if successful, and None if not.
    :param base_filename:
    :return:
    """
    try:
        return gzip.open(base_filename + '.gz', mode)
    except (IOError, OSError):
        try:
            return open(base_filename, mode)
        except (IOError, OSError):
            return None


# ***********************************************************************************************************************
# Classes for wrapping genome data
# ***********************************************************************************************************************

class GenomeSequence(object):
    """
    Computes offsets into a single fasta file containing a whole genome, for each sequence, then extracts subsequences from the file as needed
    """

    def __init__(self, fasta_filename):
        self.offsets = {}
        self.fasta_filename = fasta_filename
        self.fasta_file = open(fasta_filename, 'rU')

        cur_pos = 0
        for line in self.fasta_file:
            cur_pos += len(line)
            if line[0] == '>':
                self.offsets[toolbox.parse_chromosome_ID(line.split(' ')[0][1:])] = cur_pos

    def __del__(self):
        self.fasta_file.close()

    def extractSequence(self, chrom, start, end):
        self.fasta_file.seek(self.offsets[chrom] + start)
        # ToDO: replace the over-read -> subset method with the examine and compute method of GenomeSequenceSet
        return self.fasta_file.read((end - start) * 2).replace('\n', '')[
               :end - start]  # read more than necessary, remove CR/LF and return the correct length


class GenomeSequenceSet(object):
    """
    Computes offsets into a FASTA file for each sequence, then extracts subsequences from the file as needed.

    Assumes all sequences are stored one per file in the specified folder.

    If GZIPPED is True, assume FASTA files are gzipped.
    """
    GZIPPED = True

    def __init__(self, fasta_folder=FASTA_FOLDER, gzipped=GZIPPED_FASTA):
        self.fasta_folder = fasta_folder
        self.offsets = {}
        self.gzipped = gzipped
        if len(self.get_contig_names()) == 0:
            raise Exception('Couldn\'t find any chromosomes in {}!'.format(self.fasta_folder))

    def extract_sequence(self, contig, start, end):
        """
        Get sequence of a genomic region. Assuming the sequences are stored
        in a separate file per chromosome, we examine the first few lines of the file
        to compute offsets into the file, then read and return the appropriate region.

        If doing this in a high-throughput fashion it may save some time to pre-compute
        the offsets and store them somewhere.
        """
        assert end > start
        # identify file:
        contig_fname = os.path.join(self.fasta_folder,
                                    '{}{}{}'.format(FASTA_FNAME_PREFIX, contig, FASTA_FNAME_SUFFIX))

        if self.gzipped:
            contig_fname += '.gz'
            fasta_file = gzip.open(contig_fname, 'r')
        else:
            fasta_file = open(contig_fname, 'r')

        # examine the file to determine header line length and data line length (again, assumed constant)
        header = fasta_file.readline()
        header_size = len(header)

        first_line = fasta_file.readline()
        line_size = len(first_line)

        start_loc = compute_fasta_offset(sequence_location=start, header_size=header_size, line_size=line_size)
        end_loc = compute_fasta_offset(sequence_location=end, header_size=header_size, line_size=line_size)

        fasta_file.seek(start_loc)
        seq = fasta_file.read(end_loc - start_loc).replace('\n', '')
        fasta_file.close()
        # print seq

        return seq

    def get_contig_names(self):
        """
        Look in the FASTA folder and return the names of all the contigs for which we have sequences.
        :return:
        """
        contig_names = []
        for filename in os.listdir(self.fasta_folder):
            # print(filename, filename.startswith(self.FASTA_FNAME_PREFIX), filename.endswith(self.FASTA_FNAME_SUFFIX))
            if filename.startswith(FASTA_FNAME_PREFIX) and filename.endswith(FASTA_FNAME_SUFFIX):
                contig_names.append(filename[len(FASTA_FNAME_PREFIX):-len(FASTA_FNAME_SUFFIX)])
            elif filename.startswith(FASTA_FNAME_PREFIX) and filename.endswith(FASTA_FNAME_SUFFIX + '.gz'):
                contig_names.append(filename[len(FASTA_FNAME_PREFIX):-len(FASTA_FNAME_SUFFIX + '.gz')])

        return contig_names

    def get_contig(self, contig_name):
        """
        Reads the entire contig sequence and returns it as a string
        :param contig_name:
        :return:
        """
        contig_fname = os.path.join(self.fasta_folder,
                                    '{}{}{}'.format(FASTA_FNAME_PREFIX, contig_name, FASTA_FNAME_SUFFIX))

        print(('Loading sequence of contig {} ...'.format(contig_name)))

        if self.gzipped:
            contig_fname += '.gz'
            fasta_file = gzip.open(contig_fname, 'rt')
        else:
            fasta_file = open(contig_fname, 'rt')

        header_line = fasta_file.readline()

        if header_line.startswith('>'):
            return fasta_file.read().replace('\n', '')
        else:
            raise Exception('Contig file {} does not appear to be a valid FASTA file'.format(contig_fname))

    def get_contig_size(self, contig_name):
        """
        Returns the size of a single contig
        :param contig_name:
        :return:
        """
        return len(self.get_contig(contig_name))

    def get_all_contig_sizes(self):
        """
        Returns a dictionary, keyed by contig name, containing the sizes of all of the contigs
        :return:
        """
        contig_sizes = {}
        for contig_name in self.get_contig_names():
            contig_sizes[contig_name] = self.get_contig_size(contig_name)
        return contig_sizes


class IntervalDict(object):
    """
    This class stores genomic regions and their locations in a way that
     facilitates indexing by region_id or location. It supports setting and deleting, and querying by
     position with the .overlapping() method.
    """

    def __init__(self, interval_dict={}):
        """
        Creates a new IntervalDict, optionally populating with the regions in <interval_dict>

        :param interval_dict:
        :return:
        """
        self._regions = collections.OrderedDict()
        self._locations = {}
        for region_id, region in list(interval_dict.items()):
            self.__setitem__(region_id, region)

    @property
    def locations(self):
        return self._locations

    def __getitem__(self, region_id):
        return self._regions[region_id]

    def __setitem__(self, region_id, new_region):
        assert 'chrom' in new_region
        assert 'start' in new_region
        assert 'end' in new_region
        assert new_region['end'] > new_region['start']

        # if we are rewriting this region with different coordinates, we need to first delete it from the location tree
        if region_id in self._regions and (
                        new_region['start'] != self._regions[region_id]['start'] or new_region['end'] !=
                    self._regions[region_id]['end']):
            self.__delitem__(region_id)

        self._regions[region_id] = new_region

        # now add the updated region to the location tree
        if new_region['chrom'] not in self._locations:
            self._locations[new_region['chrom']] = intervaltree.IntervalTree()
        # print new_region['start'], new_region['end'], region_id
        self._locations[new_region['chrom']].addi(new_region['start'], new_region['end'], region_id)

    def __delitem__(self, region_id):
        self._locations[self._regions[region_id]['chrom']].removei(self._regions[region_id]['start'],
                                                                   self._regions[region_id]['end'], region_id)
        del (self._regions[region_id])

    def __len__(self):
        return len(self._regions)

    def __repr__(self):
        repr_text = ''
        for region_id, region in list(self._regions.items()):
            repr_text += '{}: {}\n'.format(region_id, ', '.join(
                    ['='.join([str(atom) for atom in item]) for item in list(region.items())]))
        return repr_text

    def __iter__(self):
        return iter(list(self._regions.keys()))

    def keys(self):
        return list(self._regions.keys())

    def values(self):
        return list(self._regions.values())

    def items(self):
        return list(self._regions.items())

    def iterkeys(self):
        return iter(list(self._regions.keys()))

    def itervalues(self):
        return iter(list(self._regions.values()))

    def iteritems(self):
        return iter(list(self._regions.items()))

    # @classmethod
    # def myclass(cls):
    #     return cls

    def emptyCopy(self):
        return IntervalDict()

    def shallowCopy(self):
        new_copy = self.emptyCopy()
        new_copy._locations = self._locations
        new_copy._regions = self._regions
        return new_copy

    def deepCopy(self):
        new_copy = self.emptyCopy()
        new_copy._regions = collections.OrderedDict(list(self._regions.items()))
        new_copy._locations = intervaltree.IntervalTree(list(self._locations.items()))

    def overlapping(self, reference, start, end, strict=False):
        """
        If <strict> is False (default), returns a new RegionDict of all regions overlapping the query region by at least one base pair
        If <strict> is True, return a new RegionDict of all regions completely enclosed by the query region
        :param reference:
        :param start:
        :param end:
        :param strict:
        :return:
        """
        result = self.emptyCopy()
        if start or end:
            for overlap in self._locations[reference].search(start, end, strict=strict):
                result[overlap.data] = self._regions[overlap.data]
        else:
            for overlap in self._locations[reference]:
                result[overlap.data] = self._regions[overlap.data]
        return result

    def intersection(self, other):
        """
        Returns the regions in self that overlap with <other>
        :param other:
        :return:
        """
        start_time = datetime.datetime.now()
        result = self.emptyCopy()
        for chrom in self._locations:
            for location in self._locations[chrom]:
                if other.locations[chrom].search(location):
                    result[location.data] = self._regions[location.data]
        print(('Intersection done in {}'.format(datetime.datetime.now() - start_time)))
        return result

    def __and__(self, other):
        return self.intersection(other)

    def difference(self, other):
        """
        Returns the regions in self that do not overlap with <other>
        :param other:
        :return:
        """
        start_time = datetime.datetime.now()
        result = self.emptyCopy()
        for chrom in self._locations:
            for location in self._locations[chrom]:
                if not other.locations[chrom].search(location):
                    result[location.data] = self._regions[location.data]
        return result

    def __sub__(self, other):
        return self.difference(other)

        # ToDo: Implement other set operations including union (need to generate new region_ids)

class IntervalDataFrame(object):
    """
    This class stores genomic regions and their locations in a way that
     facilitates indexing by region_id or location. It supports setting and deleting, and querying by
     position with the .overlapping() method.


    """
    #ToDo: Implement this class
    def __init__(self, interval_dict={}):
        """
        Creates a new IntervalDict, optionally populating with the regions in <interval_dict>

        :param interval_dict:
        :return:
        """
        self._regions = pandas.DataFrame()
        self._locations = {}
        for region_id, region in list(interval_dict.items()):
            self.__setitem__(region_id, region)

    @property
    def locations(self):
        return self._locations

    def __getitem__(self, region_id):
        return self._regions[region_id]

    def __setitem__(self, region_id, new_region):
        assert 'chrom' in new_region
        assert 'start' in new_region
        assert 'end' in new_region
        assert new_region['end'] > new_region['start']

        # if we are rewriting this region with different coordinates, we need to first delete it from the location tree
        if region_id in self._regions and (
                        new_region['start'] != self._regions[region_id]['start'] or new_region['end'] !=
                    self._regions[region_id]['end']):
            self.__delitem__(region_id)

        self._regions[region_id] = new_region

        # now add the updated region to the location tree
        if new_region['chrom'] not in self._locations:
            self._locations[new_region['chrom']] = intervaltree.IntervalTree()
        # print new_region['start'], new_region['end'], region_id
        self._locations[new_region['chrom']].addi(new_region['start'], new_region['end'], region_id)

    def __delitem__(self, region_id):
        self._locations[self._regions[region_id]['chrom']].removei(self._regions[region_id]['start'],
                                                                   self._regions[region_id]['end'], region_id)
        del (self._regions[region_id])

    def __len__(self):
        return len(self._regions)

    def __repr__(self):
        repr_text = ''
        for region_id, region in list(self._regions.items()):
            repr_text += '{}: {}\n'.format(region_id, ', '.join(
                    ['='.join([str(atom) for atom in item]) for item in list(region.items())]))
        return repr_text

    def __iter__(self):
        return iter(list(self._regions.keys()))

    def keys(self):
        return list(self._regions.keys())

    def values(self):
        return list(self._regions.values())

    def items(self):
        return list(self._regions.items())

    def iterkeys(self):
        return iter(list(self._regions.keys()))

    def itervalues(self):
        return iter(list(self._regions.values()))

    def iteritems(self):
        return iter(list(self._regions.items()))

    def overlapping(self, reference, start, end, strict=False):
        """
        If <strict> is False (default), returns a new RegionDict of all regions overlapping the query region by at least one base pair
        If <strict> is True, return a new RegionDict of all regions completely enclosed by the query region
        :param reference:
        :param start:
        :param end:
        :param strict:
        :return:
        """
        results = IntervalDict()
        if start or end:
            for overlap in self._locations[reference].search(start, end, strict=strict):
                results[overlap.data] = self._regions[overlap.data]
        else:
            for overlap in self._locations[reference]:
                results[overlap.data] = self._regions[overlap.data]
        return results

    def intersection(self, other):
        """
        Returns the regions in self that overlap with <other>
        :param other:
        :return:
        """
        start_time = datetime.datetime.now()
        result = IntervalDict()
        for chrom in self._locations:
            for location in self._locations[chrom]:
                if other.locations[chrom].search(location):
                    result[location.data] = self._regions[location.data]
        print(('Intersection done in {}'.format(datetime.datetime.now() - start_time)))
        return result

    def __and__(self, other):
        return self.intersection(other)

    def difference(self, other):
        """
        Returns the regions in self that do not overlap with <other>
        :param other:
        :return:
        """
        start_time = datetime.datetime.now()
        result = IntervalDict()
        for chrom in self._locations:
            for location in self._locations[chrom]:
                if not other.locations[chrom].search(location):
                    result[location.data] = self._regions[location.data]
        return result

    def __sub__(self, other):
        return self.difference(other)

        # ToDo: Implement other set operations including union (need to generate new region_ids)



class RegionSet(IntervalDict):
    #ToDo: make this inherit from IntervalDict
    """
    A RegionSet is an ordered nested dictionary (top level keyed by an id field
    ordered by chromosome, then by peak start position)

    region_id

    The items in the dictionary are dictionaries of region attributes:

    Core fields:
        chromosome
        start
        end
        strand
        score
        sequence
    Auxillary fields (changes depending on source)
        summit (absolute)
        foldchange (height)
        pval
        qval


    Implements methods for loading from a bed file and obtaining sequence using bedtools
    """
    HOMER_FIELD_MODEL = {
        'Start': 'start',
        'End': 'end',
        'Chr': 'chrom',
        'Strand': 'strand'
    }

    def __init__(self, interval_dict={}, name='', species='', fasta_folder='',
                 chromosome_dialect=DEFAULT_CHROMOSOME_DIALECT):
        super(RegionSet, self).__init__(interval_dict=interval_dict)
        self.name = name
        self.species = species
        self.chromosome_dialect = chromosome_dialect
        self.comment = ''

        if not fasta_folder:
            fasta_folder = os.path.join(GENOMIC_DATA_BASEPATH, SPECIES_DATA[self.species]['ensembl_build'], 'fasta')

        self.fasta_folder = fasta_folder
        self.genome_sequence = GenomeSequenceSet(fasta_folder=fasta_folder)

    @staticmethod
    def from_dict(region_dictionary, name='', species='', fasta_folder='',
                  chromosome_dialect=DEFAULT_CHROMOSOME_DIALECT):
        """
        Returns a RegionSet containing the regions defined in <region_dictionary>

        :param region_dictionary:
        :param name:
        :param species:
        :param fasta_folder:
        :param chromosome_dialect:
        :return:
        """
        new_regionset = RegionSet(interval_dict=region_dictionary,
                                  name=name,
                                  species=species,
                                  fasta_folder=fasta_folder,
                                  chromosome_dialect=chromosome_dialect)

        return new_regionset

    @staticmethod
    def from_macs2(macs2_peak_filename, name='', species='', fasta_folder='',
                   chromosome_dialect=DEFAULT_CHROMOSOME_DIALECT):
        """
        Returns a RegionSet constructed from the MACS2 peaks specified in <macs2_peak_filename>

        :param macs2_peak_filename:
        :param name:
        :param species:
        :param fasta_folder:
        :param chromosome_dialect:
        :return:
        """
        start_time = datetime.datetime.now()

        peak_dict = {}

        with open(macs2_peak_filename, 'rt') as bed_file:
            print(('Loading peaks from {}'.format(macs2_peak_filename)))
            # check for header line:
            try:
                header_line = bed_file.readline().strip()
                header_items = dict(
                        ((item.split('=')[0], item.split('=')[1].strip('"')) for item in header_line.split(' ')[1:]))

                if not name:
                    name = header_items['description'].split('/')[-1]
            except KeyError:
                bed_file.seek(0)

            for line in bed_file:
                peak = {}
                chrom, start, end, raw_id, dummy, dummy, foldchange, pval, qval, summit = line.split('\t')
                peak_id = raw_id.split('/')[-1]
                assert peak_id not in peak_dict
                peak['chrom'] = convert_chroms(chrom, chromosome_dialect)
                peak['start'] = int(start)
                peak['end'] = int(end) - 1  # convert semi-open intervals of BEDs into closed intervals
                peak['strand'] = 0
                peak['foldchange'] = float(foldchange)
                peak['pval'] = float(pval)
                peak['qval'] = float(qval)
                peak['summit'] = int(summit) + peak['start']
                # new_regionset._regions[peak_id] = peak
                peak_dict[peak_id] = peak

        new_regionset = RegionSet.from_dict(peak_dict,
                                            name=name,
                                            species=species,
                                            fasta_folder=fasta_folder,
                                            chromosome_dialect=chromosome_dialect)

        print(('Done loading {} regions in {}'.format(len(new_regionset), datetime.datetime.now() - start_time)))
        return new_regionset

    @staticmethod
    def from_basic_bed(bed_filename, name='', species='', fasta_folder='',
                       chromosome_dialect=DEFAULT_CHROMOSOME_DIALECT):
        """
        Returns a RegionSet constructed from a simple 6-field BED file

        :param self:
        :param macs2_peak_filename:
        :return:
        """
        start_time = datetime.datetime.now()

        peak_dict = {}

        with open(bed_filename, 'rt') as bed_file:
            print(('Loading regions from {}'.format(bed_filename)))
            # check for header line:
            try:
                header_line = bed_file.readline().strip()
                header_items = dict(
                        ((item.split('=')[0], item.split('=')[1].strip('"')) for item in header_line.split(' ')[1:]))

                if not name:
                    name = header_items['description'].split('/')[-1]
            except KeyError:
                bed_file.seek(0)

            for line in bed_file:
                peak = {}
                chrom, start, end, raw_id, dummy, strand = line.strip().split('\t')
                peak_id = raw_id
                assert peak_id not in peak_dict
                peak['chrom'] = convert_chroms(chrom, chromosome_dialect)
                peak['start'] = int(start)
                peak['end'] = int(end) - 1  # convert semi-open intervals of BEDs into closed intervals
                peak['strand'] = STRAND_TO_INT[strand]
                # new_regionset._regions[peak_id] = peak
                peak_dict[peak_id] = peak

        new_regionset = RegionSet.from_dict(peak_dict,
                                            name=name,
                                            species=species,
                                            fasta_folder=fasta_folder,
                                            chromosome_dialect=chromosome_dialect)

        print(('Done loading {} regions in {}'.format(len(new_regionset), datetime.datetime.now() - start_time)))
        return new_regionset

    @staticmethod
    def from_extended_bed(bed_filename, name='', species='', fasta_folder='',
                          chromosome_dialect=DEFAULT_CHROMOSOME_DIALECT):
        """
        Returns a RegionSet constructed from an extended BED file with additional fields

        :param self:
        :param macs2_peak_filename:
        :return:
        """
        start_time = datetime.datetime.now()

        peak_dict = {}

        with open(bed_filename, 'rt') as bed_file:
            print(('Loading regions from {}'.format(bed_filename)))
            # check for header line:
            try:
                header_line = bed_file.readline().strip()
                header_items = dict(
                        ((item.split('=')[0], item.split('=')[1].strip('"')) for item in header_line.split(' ')[1:]))

                if not name:
                    name = header_items['description'].split('/')[-1]
            except KeyError:
                bed_file.seek(0)

            for line in bed_file:
                peak = {}
                chrom, start, end, raw_id, dummy, strand = line.strip().split('\t')
                peak_id = raw_id
                assert peak_id not in peak_dict
                peak['chrom'] = convert_chroms(chrom, chromosome_dialect)
                peak['start'] = int(start)
                peak['end'] = int(end) - 1  # convert semi-open intervals of BEDs into closed intervals
                peak['strand'] = STRAND_TO_INT[strand]

                # ToDo: Copy remaining fields into peak

                # new_regionset._regions[peak_id] = peak
                peak_dict[peak_id] = peak

        new_regionset = RegionSet.from_dict(peak_dict,
                                            name=name,
                                            species=species,
                                            fasta_folder=fasta_folder,
                                            chromosome_dialect=chromosome_dialect)

        print(('Done loading {} regions in {}'.format(len(new_regionset), datetime.datetime.now() - start_time)))

        return new_regionset

    @staticmethod
    def from_homer_old(self, homer_peak_filename, name='', species='', fasta_folder='',
                       chromosome_dialect=DEFAULT_CHROMOSOME_DIALECT):
        """
        Returns a new RegionSet constructed from the Homer-formatted peak file in <homer_peak_filename>

        :param self:
        :param homer_peak_filename:
        :param name:
        :param species:
        :param fasta_folder:
        :param chromosome_dialect:
        :return:
        """

        start_time = datetime.datetime.now()
        new_regionset = RegionSet(name=name,
                                  species=species,
                                  fasta_folder=fasta_folder,
                                  chromosome_dialect=chromosome_dialect)

        with open(homer_peak_filename, 'rU') as bed_file:
            print(('Loading HOMER peaks from {}'.format(homer_peak_filename)))

            # skip over comment lines:
            line = bed_file.readline().strip()
            while line.startswith('#') and not line.startswith('#PeakID'):
                line = bed_file.readline().strip()

            # parse header_line
            assert line.startswith('#PeakID')

            field_names = line[1:].split('\t')
            # PeakID chr     start   end     strand  Normalized Tag Count    Not used        findPeaks Score Fold Change vs Local    p-value vs Local        Clonal Fold Change

            reader = csv.DictReader(bed_file, fieldnames=field_names, dialect=csv.excel_tab)
            # print field_names

            peak_dict = {}

            for line_idx, parsed_line in enumerate(reader):
                if line_idx % REPORTING_INTERVAL == 0:
                    print(('\tLoading peak {} ...'.format(line_idx + 1)))
                # print parsed_line
                peak = {}
                peak_id = parsed_line['PeakID']
                assert peak_id not in self._regions
                peak['chrom'] = convert_chroms(parsed_line['chr'], self.chromosome_dialect)
                peak['start'] = int(parsed_line['start'])
                peak['end'] = int(parsed_line['end']) - 1  # convert semi-open intervals of BEDs into closed intervals
                peak['foldchange'] = float(parsed_line['Fold Change vs Local'])
                peak['pval'] = float(parsed_line['p-value vs Local'])
                peak['qval'] = numpy.NaN
                peak['summit'] = numpy.NaN
                peak['tag_count'] = float(parsed_line['Normalized Tag Count'])
                peak['score'] = float(parsed_line['findPeaks Score'])
                # self._regions[peak_id] = peak
                peak_dict[peak_id] = peak
            new_regionset._regions = IntervalDict(peak_dict)
            print(('Done loading {} peaks in {}'.format(len(new_regionset), datetime.datetime.now() - start_time)))

        return new_regionset

    @staticmethod
    def from_homer(homer_peak_filename, name='', species='', fasta_folder='',
                   chromosome_dialect=DEFAULT_CHROMOSOME_DIALECT):
        """
        Returns a new RegionSet constructed from the Homer-formatted peak file in <homer_peak_filename>

        :param self:
        :param homer_peak_filename:
        :param name:
        :param species:
        :param fasta_folder:
        :param chromosome_dialect:
        :return:
        """

        start_time = datetime.datetime.now()

        print(('Loading HOMER peaks from {}'.format(homer_peak_filename)))
        with open(homer_peak_filename, 'rU') as bed_file:
            peak_df = pandas.read_csv(homer_peak_filename, sep='\t', index_col=0)
            peak_df.rename(columns=RegionSet.HOMER_FIELD_MODEL, inplace=True)
            peak_dict = peak_df.T.to_dict()

        new_regionset = RegionSet.from_dict(region_dictionary=peak_dict,
                                            name=name,
                                            species=species,
                                            fasta_folder=fasta_folder,
                                            chromosome_dialect=chromosome_dialect)

        print(('Done loading {} peaks in {}'.format(len(new_regionset), datetime.datetime.now() - start_time)))

        return new_regionset

    # def query_by_location(self, contig, start, end, strand=0, strict=False):
    #     """
    #     Returns a dictionary of regions, keyed by ID, that overlap the queried region by at least 1 base pair (if
    #     <strict> is False (default), or completely enclosed by the query region if <strict> is True).
    #     :return:
    #     """
    #     overlapping_regions = self.overlapping(contig, start, end, strict=strict)
    #     return overlapping_regions

    # @property
    # def regions(self):
    #     return self._regions

    # @regions.setter
    # def regions(self, regions):
    #     self._regions = regions


    def to_bed(self, bed_filename):
        """
        Export the regions to a BED file.

        :param bed_filename:
        :return:
        """
        start_time = datetime.datetime.now()

        print(('Saving regions to {} ...'.format(bed_filename)))

        fieldnames = ['peak_id', 'chrom', 'start', 'end', 'not_used', 'strand'] + sorted(
                set(list(self.values())[0].keys()).difference({'chrom', 'start', 'end', 'strand'}))

        with open(bed_filename, 'wt') as bed_file:
            output_writer = csv.DictWriter(bed_filename, fieldnames=fieldnames, dialect=csv.excel_tab)
            output_writer.writeheader()
            for region_id, region in list(self.items()):
                row = region.copy()
                row['peak_id'] = region_id
                output_writer.writerow(row)

        print(('Done in {}'.format(datetime.datetime.now() - start_time)))

    def populate_region_sequences(self):
        """
        Adds the strand-specific sequence of the region as a field

        :return:
        """
        start_time = datetime.datetime.now()
        print(('Loading peak sequences from {}'.format(self.fasta_folder)))
        # print seqs.keys()
        for region_id, region in list(self.items()):
            region['sequence'] = self.get_sequence(region_id)
        print(('Done loading peak sequences in {}'.format(datetime.datetime.now() - start_time)))

    def get_sequence(self, region_id):
        """
        Return the sequence of a single region.
        :param region_id:
        :return:
        """
        base_sequence = self.genome_sequence.extract_sequence(contig=self[region_id]['chrom'],
                                                              start=self[region_id]['start'],
                                                              end=self[region_id]['end'])

        if self[region_id]['strand'] == -1:
            return toolbox.rev_complement(base_sequence)
        else:
            return base_sequence

    def trim_peaks(self, window_size):
        """
        Trims all peaks to <window_size>, centered on the peak summit.

        :param window_size:
        :return:
        """
        start_time = datetime.datetime.now()
        half_window = int(window_size / 2)
        print(('Trimming all peaks to a {} bp window centered around the peak summit'.format(window_size)))
        for peak_id in self:
            new_peak = self[peak_id].copy()
            new_peak['start'] = max(self[peak_id]['summit'] - half_window, 0)
            new_peak['end'] = min(self[peak_id]['summit'] + half_window, self[peak_id]['end'])
            self._regions[peak_id] = new_peak
        print(('Done trimming peaks in {}'.format(datetime.datetime.now() - start_time)))

    def lift_over(self, new_species, translators):
        """
        Lifts over all peak coordinates to a new build.

        :param new_species:
        :param translators:
        :return:
        """
        start_time = datetime.datetime.now()
        source_build = SPECIES_DATA[self.species]['ucsc_build']
        dest_build = SPECIES_DATA[new_species]['ucsc_build']
        lo_peakset = RegionSet(name='{} lifted over from {} to {}'.format(self.name, self.species, new_species),
                               species=new_species)
        for peak_id in self:
            lo_peak = translators.liftover_peak(source_build=source_build, dest_build=dest_build, source_peak=(
                self[peak_id]['chrom'], self[peak_id]['start'], self[peak_id]['end']))
            if lo_peak:
                new_region = {'chrom': lo_peak[0], 'start': lo_peak[1], 'end': lo_peak[2]}
                # ToDo: copy the other field data over
                lo_peakset._regions[peak_id] = new_region

        print(('Done lifting over in {}'.format(datetime.datetime.now() - start_time)))

        return lo_peakset

    def compute_pileup_enrichment(self, pileup, score_name, scoring_method='mean'):
        """
        Computes an 'enrichment' score for each peak region based on the contents of that region in the given <pileup> object,
        then stores that score in a key named <score_name> for each peak.

        Currently supported scoring methods:
            mean: take the mean of all pileup values in the peak region
        """
        start_time = datetime.datetime.now()
        print(('Computing enrichment for all peaks. Method: {}'.format(scoring_method)))
        missing_chroms = set([])
        if scoring_method == 'mean':
            for peak_id in self:
                cur_peak = self[peak_id]
                if cur_peak['chrom'] in pileup.pileups:
                    cur_peak[score_name] = numpy.mean(
                            pileup.pileups[cur_peak['chrom']][cur_peak['start']:cur_peak['end']])
                else:
                    cur_peak[score_name] = None
                    missing_chroms.add(cur_peak['chrom'])
        print(('Done in {}.'.format(datetime.datetime.now() - start_time)))
        print(('The following chromosomes were not found in the pileups: {}'.format(', '.join(missing_chroms))))

    def threshold_by(self, threshold_field, threshold_value, keep_larger=True):
        """
        Returns a new peakset containing only peaks where <threshold_variable> is greater than
        <threshold_value> (if <keep_larger>), or lesser (otherwise).
        """
        start_time = datetime.datetime.now()
        print(('Thresholding {} by {} {} than {}'.format(self.name, threshold_field, ('less', 'greater')[keep_larger],
                                                         threshold_value)))
        new_set = self.empty_copy()
        peak_count = 0
        for peak_id in self._regions:
            if keep_larger:
                if self[peak_id][threshold_field] > threshold_value:
                    new_set._regions[peak_id] = self[peak_id]
                    peak_count += 1
            else:
                if self[peak_id][threshold_field] < threshold_value:
                    new_set._regions[peak_id] = self[peak_id]
                    peak_count += 1
        print(('Kept {} out of {} regions in {}'.format(peak_count, len(self._regions),
                                                        datetime.datetime.now() - start_time)))
        return new_set

    def define_promoters(self, upstream_threshold, downstream_threshold):
        """
        Returns a new RegionSet consisting of a
        :param upstream_threshold:
        :param downstream_threshold:
        :return:
        """
        start_time = datetime.datetime.now()
        promoter_regions = self.empty_copy()

        for region_id, region in list(self.items()):
            promoter_id = region_id + '_promoter'
            promoter = {}
            for field in region:
                if field == 'start':
                    if region['strand'] == -1:
                        # promoter['start'] = min(region['end'] + upstream_threshold, self.chrom_lengths[region['chrom']])
                        promoter['end'] = region['end'] + upstream_threshold
                    else:
                        # promoter['start'] = max(region['start'] - upstream_threshold, 0)
                        promoter['start'] = region['start'] - upstream_threshold
                elif field == 'end':
                    if region['strand'] == -1:
                        # promoter['end'] = max(region['end'] - downstream_threshold, 0)
                        promoter['start'] = region['end'] - downstream_threshold
                    else:
                        # promoter['end'] = min(region['start'] + downstream_threshold,
                        #                       self.chrom_lengths[region['chrom']])
                        promoter['end'] = region['start'] + downstream_threshold
                else:
                    promoter[field] = region[field]
            promoter_regions[promoter_id] = promoter
        print(('Done in {}'.format(datetime.datetime.now() - start_time)))
        return promoter_regions

    def empty_copy(self):
        """
        Returns a copy of the current object with the same meta data but no data

        :return:
        """
        return RegionSet(name=self.name, species=self.species, fasta_folder=self.fasta_folder,
                         chromosome_dialect=self.chromosome_dialect)

    def shallow_copy(self):
        """
        Returns a copy of the current object with the same meta data and links to the same data.

        :return:
        """
        copy = self.empty_copy()
        copy._regions = self._regions
        copy._locations = self._locations
        return copy

    def deep_copy(self):
        """
        Returns a copy of the current object with the same meta data and new copies of the data

        :return:
        """
        copy = self.empty_copy()
        for region_id, region in list(self._regions.items()):
            copy[region_id] = region
        return copy

    def sort_by(self, sort_field, reverse=False):
        """
        Sort the regions by the specified field.

        :param sort_field:
        :param reverse:
        :return:
        """
        start_time = datetime.datetime.now()
        print(('Sorting in {} order by {}'.format(('normal', 'reverse')[bool(reverse)], sort_field)))
        self._regions = collections.OrderedDict(sorted(list(self._regions.items()), key=lambda x: x[1][sort_field], reverse=reverse))
        print(('Done in {}'.format(datetime.datetime.now() - start_time)))

    def difference(self, other):
        result = super(RegionSet, self).difference(other)
        result.name = '{}_difference_{}'.format(self.name, other.name)
        return result

    def __sub__(self, other):
        return self.difference(other)

    def intersection(self, other):
        result = super(RegionSet, self).intersection(other)
        result.name = '{}_intersected_{}'.format(self.name, other.name)
        return result

    def __and__(self, other):
        return self.intersection(other)

    def get_region_sizes(self):
        return [region['end'] - region['start'] for region in list(self._regions.values())]


class RegionOverlaps(object):
    """
    Container for a nested dictionary that maps region_ids from one named RegionSet to another based on overlap. Also includes
    coordinates for the overlap relative to the destination build.

    Structure is:

        {source_regionset_name:
            {source_region_id:
                {destination_regionset_name:
                    [list of dicitonaries:
                        {dest_region_id, dest_start, dest_end, dest_sequence (optional)}
                    ]
                }
            }
        }
    Implements methods to generate overlap mappings.
    """

    def __init__(self, source_regions, dest_regions, translators=None, reference_genome=None, min_overlap=0):
        self.overlaps = {}
        self.populate(source_regions, dest_regions, translators, reference_genome, min_overlap)

    def populate(self, source_regions, dest_regions, translators=None, reference_genome=None, min_overlap=0):
        """
        Call to populate the overlap dictionary with a source-destination pair of peaksets.

        :param source_regions:
        :param dest_regions:
        :param translators:
        :param reference_genome:
        :return:
        """
        print(('Computing overlaps from peak set {} to {}...'.format(source_regions.name, dest_regions.name)))
        if source_regions.species != dest_regions.species and not translators:
            raise Exception('Source and destination species are not the same, you must specify a BuildMapper object!')

        source_region_list = list(source_regions.peaks.values())
        dest_region_list = list(dest_regions.peaks.values())

        # first we need to reorganize by chromosome:
        dest_region_dict = {}
        for region in dest_region_list:
            if region['chrom'] not in dest_region_dict:
                dest_region_dict[region['chrom']] = []
            dest_region_dict[region['chrom']].append((region['id'], region['start'], region['end']))

        source_region_dict = {}
        # lift over the source peaks to the destination species (if different)
        for region in source_region_list:
            if region['chrom'] not in source_region_dict:
                source_region_dict[region['chrom']] = []
            if source_regions.species == dest_regions.species:
                new_region = (region['id'], region['start'], region['end'])
            else:
                new_region = translators.liftover_peak(SPECIES_DATA[source_regions.species]['ucsc_build'],
                                                       SPECIES_DATA[dest_regions.species]['ucsc_build'],
                                                       (region['chrom'], region['start'], region['end']))
            source_region_dict[region['chrom']].append(new_region)

        # print source_region_dict
        #         print dest_region_dict

        # get overlaps
        overlap_dict = {}
        for chrom in source_region_dict:
            #             print chrom, chrom in dest_region_dict
            if chrom in dest_region_dict:
                overlap_dict[chrom] = intervaloverlaps.interval_overlaps(source_region_dict[chrom],
                                                                         dest_region_dict[chrom])

        # initialize internal dictionary with empty entries for all source peaks
        if source_regions.name not in self.overlaps:
            self.overlaps[source_regions.name] = {}

        for region in source_region_list:
            self.overlaps[source_regions.name][region['id']] = {}
            self.overlaps[source_regions.name][region['id']][dest_regions.name] = []

        # now add the overlaps to the internal dictionary
        for chrom in overlap_dict:
            for overlap in overlap_dict[chrom]:
                if overlap[3] - overlap[2] > min_overlap:
                    new_overlap = {'dest_peak_id': overlap[1], 'dest_start': overlap[2], 'dest_end': overlap[3]}
                    if reference_genome:
                        new_overlap['dest_sequence'] = reference_genome.exractSequence(chrom, overlap[2], overlap[3])
                    self.overlaps[source_regions.name][overlap[0]][dest_regions.name].append(new_overlap)
        print('Done.')


class Genome(object):
    """
    Serves up gene locations and sequences.
    """

    def __init__(self, fasta_folder=FASTA_FOLDER, gff_fname=GFF_FNAME, genome_info_fname=GENE_INFO_PICKLE_FNAME,
                 chromosome_dialect='ensembl', species='human', force_rebuild=False):
        self.fasta_folder = fasta_folder
        self.gff_fname = gff_fname
        self.genome_info_fname = genome_info_fname
        self.species = species
        self.chromosome_dialect = chromosome_dialect

        # initialize sequence object
        self.genome_sequence = GenomeSequenceSet(self.fasta_folder)

        # initialize gene names and coordinate data either from pre-generated
        # data or de novo from a GFF file
        # ToDo: refactor this ugly mess
        try:
            gene_info_file = find_file_gzipped(self.genome_info_fname, 'rb')
            start_time = datetime.datetime.now()
            print(('Loading gene info from {} ...'.format(genome_info_fname)))
            if gene_info_file:
                self.genes, self.gene_name_to_ensembl, self._contig_lengths = pickle.load(gene_info_file)
                gene_info_file.close()
                print(('Done in {}'.format(datetime.datetime.now() - start_time)))
            else:
                force_rebuild = True
        except (ImportError, IOError, OSError):
            force_rebuild = True
        if force_rebuild:
            start_time = datetime.datetime.now()
            print(('Generating gene info and translation data from GFF file {} ...'.format(gff_fname)))
            self._generate_dictionaries()
            print(('Done in {}'.format(datetime.datetime.now() - start_time)))

    def _generate_dictionaries(self):
        """
        Generate the internal data structures based on information in the GFF file

        :return:
        """

        gff_file = find_file_gzipped(self.gff_fname, 'rt')

        if gff_file is None:
            raise Exception('GFF file not found! Looked for {} and {}'.format(self.gff_fname, self.gff_fname + '.gz'))

        # generate from GFF
        gene_info, self.gene_name_to_ensembl = gff_to_gene_dict(gff_file)
        gff_file.close()
        self.genes = RegionSet(species=self.species, fasta_folder=self.fasta_folder,
                               chromosome_dialect=self.chromosome_dialect)
        self.genes.populate_from_dict(gene_info)

        # compute contig lengths from sequence
        self._populate_contig_lengths()

        # write out to pickle to save time in future
        with gzip.open(self.genome_info_fname + '.gz', 'wb') as gene_info_file:
            pickle.dump((self.genes, self.gene_name_to_ensembl, self._contig_lengths), gene_info_file, protocol=-1)

        print(('{} genes by Ensembl ID, {} gene symbols'.format(len(self.genes), len(self.gene_name_to_ensembl))))

    def _populate_contig_lengths(self):
        """
        Go through the FASTA files to determine the length of each contig and store this in a dictionary attribute

        :return:
        """
        self._contig_lengths = self.genome_sequence.get_all_contig_sizes()

    def get_contig_length(self, contig_name):
        """
        Returns the length of the given contig if it exists in the genome, otherwise returns None
        :param contig_name:
        :return:
        """
        if contig_name in self._contig_lengths:
            return self._contig_lengths[contig_name]
        else:
            return None

    def gene_info_by_ensembl_id(self, ensembl_id):
        """
        Return a dictionary of information fields about the gene specified
        by the given ensembl_id.

        :param ensembl_id:
        :return:
        """
        return self.genes[ensembl_id]

    def gene_info_by_name(self, gene_name):
        """
        Returns a dictionary of information fields about the gene specified
        by the given gene name. Returns None if the gene name has no Ensembl ID
        or if the Ensembl ID is not found in the info data.

        :param gene_name:
        :return:
        """
        if gene_name in self.gene_name_to_ensembl:
            ensembl_name = self.gene_name_to_ensembl[gene_name]
            if ensembl_name in self.genes:
                return self.genes[ensembl_name]
            else:
                return None
        else:
            return None

    def get_genes_by_location(self, contig, start, end, strand=0, strict=False):
        """
        Returns an ordered  dictionary of genes oerlapping the specified region. Currently ignores <strand> parameter,
         returns genes on both strands
        :param contig:
        :param start:
        :param end:
        :param strand:
        :return:
        """
        return self.genes.query_by_location(contig=contig, start=start, end=end, strand=strand, strict=strict)

    def get_dna_sequence(self, contig, start, end, strand):
        """
        Return the sequence of the specified genomic region.
        :param contig:
        :param start:
        :param end:
        :param strand:
        :return:
        """
        base_sequence = self.genome_sequence.extract_sequence(contig=contig, start=start, end=end)

        if strand == -1:
            return toolbox.rev_complement(base_sequence)
        else:
            return base_sequence

    def get_dna_sequence_by_name(self, gene_name):
        """
        Returns the genomic sequence of the specified gene name
        :param gene_name:
        :return:
        """
        ensembl_id = self.gene_name_to_ensembl[gene_name]
        return self.genes.get_sequence(ensembl_id)

    def query_by_ensembl_id(self, ensembl_id):
        """
        Return a dictionary of information fields about the gene specified
        by the given ensembl_id.

        :param ensembl_id:
        :return:
        """
        return self.genes.regions[ensembl_id]

    def query_by_gene_name(self, gene_name):
        """
        Returns a dictionary of information fields about the gene specified
        by the given gene name. Returns None if the gene name has no Ensembl ID
        or if the Ensembl ID is not found in the info data.

        :param gene_name:
        :return:
        """
        if gene_name in self.gene_name_to_ensembl:
            ensembl_name = self.gene_name_to_ensembl[gene_name]
            if ensembl_name in self.genes.regions:
                return self.genes.regions[ensembl_name]
            else:
                return None
        else:
            return None


class Variants(object):
    """
    Serves up variants from a tabix-indexed VCF file
    """
    # field mappings for various flavors of VCF
    FREE_BAYES = {'core_fields':
                      {0: ('chrom', str),
                       1: ('pos', int),
                       3: ('ref', str),
                       4: ('alt', str),
                       5: ('qual', float)},
                  'info_position': 7,
                  'info_fields': {
                      'PM': ('precious', bool),
                      'NSF': ('frameshift', bool),
                      'NSN': ('nonsense', bool),
                      'NSM': ('missense', bool),
                      'TYPE': ('type', str),
                      'ODDS': ('odds', float)}
                  }

    def __init__(self, vcf_filename, field_model=FREE_BAYES):
        self.variant_file = pysam.Tabixfile(vcf_filename)
        self.field_model = field_model

    def _parse_row(self, variant_tuple):
        variant_dict = {}
        # get core fields
        for position, (destination, parse_func) in list(self.field_model['core_fields'].items()):
            variant_dict[destination] = parse_func(variant_tuple[position])
        # get info fieds
        split_info = variant_tuple[self.field_model['info_position']].split(';')

        for field_atom in split_info:
            field, value = field_atom.split('=')
            if field in self.field_model['info_fields']:
                destination, parse_func = self.field_model['info_fields'][field]
                variant_dict[destination] = parse_func(value)

        return variant_dict

    def get_variants(self, chrom, start, end):
        variants = []
        for variant_tuple in self.variant_file.fetch(reference=chrom, start=start, end=end, parser=pysam.asTuple()):
            variants.append(self._parse_row(variant_tuple))
        return variants


def vcf_to_bed(filtered_vcf_filename, output_filename):
    """
    Extract information from the filtered VCF, interpret it and store it as a tab-delimited BED file
    """

    vcf_reader = vcf.Reader(filename=filtered_vcf_filename)

    with open(output_filename, 'wt') as outfile:
        dict_writer = csv.DictWriter(outfile,
                                     fieldnames=['chrom', 'start', 'end', 'affected_start', 'affected_end', 'ref',
                                                 'qual', 'alt', 'annotation', 'impact', 'var_type', 'var_subtype',
                                                 'gene', 'feature'],
                                     dialect=csv.excel_tab)
        for r in vcf_reader:
            row_dict = {}
            row_dict['chrom'] = r.CHROM
            row_dict['start'] = r.start
            # row_dict['POS'] = r.POS
            row_dict['end'] = r.end
            try:
                row_dict['affected_start'] = r.affected_start
                row_dict['affected_end'] = r.affected_end
            except AttributeError:
                pass
            row_dict['ref'] = r.REF
            row_dict['qual'] = r.QUAL
            row_dict['alt'] = r.ALT[0]
            # Sequence ontology
            row_dict['annotation'] = ','.join(x.split('|')[1] for x in r.INFO['ANN'])
            # {HIGH, MODERATE, LOW, MODIFIER}
            row_dict['impact'] = ','.join(x.split('|')[2] for x in r.INFO['ANN'])
            row_dict['var_type'] = r.var_type
            row_dict['var_subtype'] = r.var_subtype
            row_dict['gene'] = ','.join(x.split('|')[3] for x in r.INFO['ANN'])
            row_dict['feature'] = ','.join(x.split('|')[5] for x in r.INFO['ANN'])

            dict_writer.writerow(row_dict)


def bgzip_and_tabix(bed_filename):
    run(['bgzip', bed_filename])
    compressed_filename = bed_filename + '.gz'
    tabix_commands = ['tabix', '-s', '0', '-b', '1', '-e', '2', '-f', compressed_filename]
    # print('tabix command line: {}'.format(' '.join(tabix_commands)))
    run(['tabix', '-s', '1', '-b', '2', '-e', '3', '-f', compressed_filename])


# linear-time algorithm for determining overlap of two lists of intervals. Need to generalize and integrate ...
def assignBinding(self, TFBS_list, ORF_list, upstream_threshold, downstream_threshold, exclude_intragenic=True,
                  one_to_many=False, use_midpoint=True):
    """
    Given two lists of tuples in the form:

        (<start>, <end>, <strand>, <name>)

    where strand has the values -1 for -, 1 for + and 0 for indeterminate, generate a list of tuples in the form:

        (<region1_name>, <region2_name>)

    for each region from list 1 whose midpoint is between <upstream_threshold> and <downstream_threshold> from the start of region 2.

    If <use_midpoint> is False, count a match when any portion of a peak falls between <upstream_threshold> and <downstream_threshold>.

    If the strand of the region from list 2 is -1, the match will be to the end of the region
    and the upstream and downstream threshold values will be reversed.

    Note: <upstream_threshold> and <downstream_threshold> must be positive.
    """

    assert upstream_threshold >= 0 and downstream_threshold >= 0

    TFBS_dict = {}
    ORF_dict = {}

    def start_idx(strand_val):
        """
        Inline to calculate the start point of a region depending on the strand orientation
        """
        return (1 - strand_val) / 2 + 1

    def end_idx(strand_val):
        """
        Inline to calculate the end point of a region depending on the strand orientation
        """
        return (1 + strand_val) / 2 + 1

    def overlap(peak, ORF, strand, upstream_threshold, downstream_threshold, use_midpoint):
        """
        Returns true if any part of peak overlaps the promoter of ORF

        There are four ways that an overlap can occur:
            1. The start point of peak is inside the promoter
            2. The end point of peak is inside the promoter
            3. The start point is upstream of the promoter and the end point is downstream
            4. Both the start point and end point of peak are inside the promoter.

        Since if case 4 is true then cases 1 and 2 are both true, we need to consider only 1-3.
        """
        if use_midpoint:
            return strand * (ORF[0] - peak[0]) <= upstream_threshold and strand * (
                ORF[0] - peak[0]) >= -downstream_threshold
        else:
            if strand * (ORF[start_idx(strand)] - peak[start_idx(strand)]) <= upstream_threshold and strand * (
                        ORF[start_idx(strand)] - peak[start_idx(strand)]) >= -downstream_threshold:
                # print ORF, peak
                return True
            elif strand * (ORF[start_idx(strand)] - peak[end_idx(strand)]) <= upstream_threshold and strand * (
                        ORF[start_idx(strand)] - peak[end_idx(strand)]) >= -downstream_threshold:
                # print '\t', ORF, peak
                return True
            elif strand * (ORF[start_idx(strand)] - peak[start_idx(strand)]) >= upstream_threshold and strand * (
                        ORF[start_idx(strand)] - peak[end_idx(strand)]) <= -downstream_threshold:
                # print '\t\t', ORF, peak
                return True
            else:
                return False

    matches = []

    for strand in [1, -1]:  # consider each strand separately
        # _print('Examining strand {}'.format(strand))
        # create a separate dictionary for this strand
        # sort by start position for + strand, end position for - strand. First field is the midpoint for region1 and the TSS for ORF
        TFBS_dict[strand] = sorted(
                [((x[0] + x[1]) / 2, x[0], x[1], x[3]) for x in TFBS_list if x[2] == strand or x[2] == 0],
                key=lambda y: y[0], reverse=bool((1 - strand) / 2))
        ORF_dict[strand] = sorted(
                [(w[(1 - strand) / 2], w[0], w[1], w[3]) for w in ORF_list if w[2] == strand or w[2] == 0],
                key=lambda z: z[0], reverse=bool((1 - strand) / 2))

        TFBS_idx = 0
        ORF_idx = 0

        # initialize appropriately depending on strand:
        previous_ORF_end = [float('-inf'), float('inf')][(1 - strand) / 2]

        # While we haven't reached the end of both lists, continue processing
        while ORF_idx < len(ORF_dict[strand]) and TFBS_idx < len(
                TFBS_dict[strand]):
            ORF = ORF_dict[strand][ORF_idx]

            # 				_print ('Considering ORF {} at {}-{}'.format(ORF[3], ORF[1], ORF[2]))
            # 				_print ('Current TFBS {}.{} at {}-{}'.format(TFBS_idx, TFBS_dict[strand][TFBS_idx][3], TFBS_dict[strand][TFBS_idx][1], TFBS_dict[strand][TFBS_idx][2]))

            # while the next TFBS is too far upstream of the current ORF, advance to the next TFBS
            while TFBS_idx < len(TFBS_dict[strand]) and (
                            strand * TFBS_dict[strand][TFBS_idx][[end_idx(strand), 0][use_midpoint]] < strand * (
                                ORF[0] - strand * upstream_threshold)):
                # 					_print ('TFBS {}.{} is {} from TSS of ORF {}'.format(TFBS_idx, TFBS_dict[strand][TFBS_idx][3], TFBS_dict[strand][TFBS_idx][0] - ORF[0], ORF[3]))

                TFBS_idx += 1
            # if TFBS_idx < len(TFBS_dict[strand]):
            # 						_print ('Advancing to TFBS {}.{} at {}-{}'.format(TFBS_idx, TFBS_dict[strand][TFBS_idx][3],TFBS_dict[strand][TFBS_idx][1], TFBS_dict[strand][TFBS_idx][2]))
            # 					else:
            # 						_print ('Last TFBS reached')

            if exclude_intragenic:  # if this is set to True, keep advancing the TFBS index until the start of the TFBS clears the end of the previous ORF
                while TFBS_idx < len(TFBS_dict[strand]) and (
                                strand * TFBS_dict[strand][TFBS_idx][
                                start_idx(strand)] < strand * previous_ORF_end):
                    # 						_print ('TFBS {}.{} is within ORF {}. Advancing to TFBS {}.{} at {}-{}'.format(TFBS_idx, TFBS_dict[strand][TFBS_idx][3], ORF_dict[strand][ORF_idx -1][3], TFBS_idx + 1, TFBS_dict[strand][TFBS_idx + 1][3], TFBS_dict[strand][TFBS_idx + 1][1], TFBS_dict[strand][TFBS_idx + 1][2]))
                    TFBS_idx += 1

            # Memorize what TFBS we're on so we can start here again on the next ORF.
            # This allows us to match multiple ORFs to each TFBS.
            start_of_TFBS_block = TFBS_idx

            # if there are any TFBSs in our promoter region, add them to the list of matches
            while TFBS_idx < len(TFBS_dict[strand]) and overlap(peak=TFBS_dict[strand][TFBS_idx], ORF=ORF,
                                                                strand=strand,
                                                                upstream_threshold=upstream_threshold,
                                                                downstream_threshold=downstream_threshold,
                                                                use_midpoint=use_midpoint):
                # 					_print ('TFBS {}.{} is {} from TSS of ORF {}, adding to matches. '.format(TFBS_idx, TFBS_dict[strand][TFBS_idx][3], TFBS_dict[strand][TFBS_idx][0] - ORF[0], ORF[3]))
                matches.append((TFBS_dict[strand][TFBS_idx][3], ORF[3]))
                TFBS_idx += 1
            # if TFBS_idx < len(TFBS_dict[strand]):
            # 						_print ('Advancing to TFBS {}.{} at {}-{}'.format(TFBS_idx, TFBS_dict[strand][TFBS_idx][3],TFBS_dict[strand][TFBS_idx][1], TFBS_dict[strand][TFBS_idx][2]))
            # 					else:
            # 						_print ('Last TFBS reached')

            if one_to_many:
                TFBS_idx = start_of_TFBS_block

            previous_ORF_end = ORF[(1 + strand) / 2 + 1]  # depends on integer division. Will break in Python 3.x
            ORF_idx += 1
    return matches


def test():
    # from pprint import pprint
    # fasta_fname = '/cellar/users/dskola/oasis_local/reference_genomes/dm3-ver5.46/dmel-all-chromosome-r5.46.fasta'
    # dmel_genome = GenomeSequence(fasta_fname)
    # test_set1 = RegionSet(bed_filename='ERR020068_peaks.narrowPeak', reference_genome=dmel_genome, name='test1')
    # pprint([(x['chrom'], x['end'] - x['start'], len(x['sequence'])) for x in list(test_set1.peaks.values())[:10]])
    pass


if __name__ == '__main__':
    test()
