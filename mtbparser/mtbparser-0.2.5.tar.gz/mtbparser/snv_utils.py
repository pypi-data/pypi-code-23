"""
Collection of different header types, specified
as enums.
"""
from enum import Enum

class SSnvHeader(Enum):
    """ Enumeration class for the different column types
    specified in the header of the somatic SNV tsv file.
    """
    CHR = "chr"
    START = "start"
    REF = "ref"
    ALT = "alt"
    ALLELE_F_TUMOR = "allele_frequency_tumor"
    COVERAGE = "coverage"
    GENE = "gene"
    BASE_CHANGE = "base_change"
    AA_CHANGE = "aa_change"
    TRANSCRIPT = "transcript"
    FUN_CLASS = "functional_class"
    EFFECT = "effect"
    HEADER_LEN = 12

class GSnvHeader(Enum):
    """ Enumeration class for the different column types
    specified in the header of the germline SNV tsv file.
    """
    CHR = "chr"
    START = "start"
    REF = "ref"
    ALT = "alt"
    GENOTYPE = "genotype"
    GENE = "gene"
    BASE_CHANGE = "base_change"
    AA_CHANGE = "aa_change"
    TRANSCRIPT = "transcript"
    FUN_CLASS = "functional_class"
    EFFECT = "effect"
    HEADER_LEN = 11

class CnvHeader(Enum):
    """ Enumeration class for the different column types
    specified in the header of the germline and somatic
    CNV tsv file.
    """
    SIZE = "size"
    TYPE = "type"
    COPY_NUMBER = "copy_number"
    GENE = "gene"
    EXONS = "exons"
    TRANSCRIPT = "transcript"
    CHR = "chr"
    START = "start"
    END = "end"
    EFFECT = "effect"
    HEADER_LEN = 10

class SsvHeader(Enum):
    """ Enumeration class for the different column types
    specified in the header of the somatic structural variants
    tsv file.
    """
    TYPE = "type"
    GENE = "gene"
    EFFECT = "effect"
    LEFT_BP = "left_bp"
    RIGHT_BP = "right_bp"
    HEADER_LEN = 5

class MetaData(Enum):
    """ Enumeration class for the different column types
    specified in the header of the metadata tsv file.
    """
    DIAGNOSIS = "diagnosis"
    TUMOR_CONTENT = "tumor_content"
    PATHOGENIC_GERMLINE = "pathogenic_germline"
    MUTATIONAL_LOAD = "mutational_load"
    CHROMOSOMAL_INSTABILITY = "chromosomal_instability"
    QUALITY_FLAGS = "quality_flags"
    REFERENCE_GENOME = "reference_genome"
    HEADER_LEN = 7
