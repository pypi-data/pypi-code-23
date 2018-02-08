import re
from Bio import Phylo
from Bio.Phylo.BaseTree import Tree
from io import StringIO
from typing import Iterator, Tuple


_REFX = re.compile( "([0-9.]+):[0-9.]+" )


def convert_file( in_filename, out_filename, in_format, out_format ):
    from Bio import AlignIO
    
    with open( in_filename, "rU" ) as input_handle:
        with open( out_filename, "w" ) as output_handle:
            alignments = AlignIO.parse( input_handle, in_format )
            AlignIO.write( alignments, output_handle, out_format )


def parse_fasta( *, text = None, file = None ) -> Iterator[Tuple[str, str]]:
    """
    Parses a FASTA file.
    Accepts multi-line sequences.
    Accepts ';' comments in the file.
    
    Nb. BioPython's SeqIO.parse doesn't handle comments for FASTA.
    
    :param text:    FASTA text 
    :param file:    Path to FASTA file 
    :return:        Tuples of sequence names and sites 
    """
    from mhelper import file_helper
    
    if file is not None:
        if text is not None:
            raise ValueError( "Cannot specify both `file` and `text` arguments to `parse_fasta`." )
        
        text = file_helper.read_all_text( file )
    elif text is None:
        raise ValueError( "Must specify either `file` or `text` arguments when calling `parse_fasta`." )
    
    heading = None
    sequence = []
    
    for line in text.split( "\n" ):
        line = line.strip()
        
        if line.startswith( ">" ):
            if heading is not None:
                yield heading, "".join( sequence )
            
            heading = line[1:]
            sequence = []
        elif not line.startswith( ";" ):
            sequence.append( line )
    
    if heading is not None:
        yield heading, "".join( sequence )


def biotree_to_newick( tree: Tree ) -> str:
    handle = StringIO()
    Phylo.write( [tree], handle, "newick" )
    result = handle.getvalue()
    
    # Work around stupid BioPython bug
    # https://github.com/biopython/biopython/issues/1315
    # TODO: Remove this fix when the issue is fixed
    result = _REFX.sub( "\\1", result )
    
    return result


def newick_to_biotree( newick ) -> Tree:
    handle = StringIO( newick )
    return Phylo.read( handle, "newick" )
