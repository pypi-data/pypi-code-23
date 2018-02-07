"""
An enum class for having a controlled
vocabulary for the different file types.
"""
from enum import Enum

class MtbFileType(Enum):
    """Maps an unique mtb file type to an enum object"""
    GERM_SNV = "_germline_snv.tsv"
    GERM_CNV = "_germline_cnv.tsv"
    SOM_SNV = "_somatic_snv.tsv"
    SOM_CNV = "_somatic_cnv.tsv"
    SOM_SV = "_somatic_sv.tsv"
    META = "_metadata.tsv"
