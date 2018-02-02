from collections import defaultdict
from typing import List, Dict, Tuple

from cluster_searcher.leca import LecaGene
from cluster_searcher.states import state
from intermake.engine.environment import MCMD


class BlastFile:
    def __init__( self, file_name: str ) -> None:
        self.file_name = file_name
        self.contents: List[BlastLine] = []
        self.lookup_by_kegg: Dict[str, List[BlastLine]] = defaultdict( list )
        
        with MCMD.action( "Loading BLAST" ) as action:
            with open( file_name, "r" ) as file_in:
                for line in file_in:
                    blast_line = BlastLine( line.strip() )
                    self.lookup_by_kegg[blast_line.query_id].append( blast_line )
                    self.contents.append( blast_line )
                    action.still_alive()


class BlastLine:
    def __init__( self, line ) -> None:
        def ___parse_david( text ) -> Tuple[str, str]:
            gene_id = text.split( "|", 1 )[1]
            return gene_id.split( "_", 1 )
        
        
        elements = line.split( "\t" )
        
        self.query_id = elements[0]
        self.barcode, self.subject_id = ___parse_david( elements[1] )
        self.percentage_identity = float( elements[2] )
        self.alignment_length = int( elements[3] )
        self.mismatches = int( elements[4] )
        self.gap_opens = int( elements[5] )
        self.query_start = int( elements[6] )
        self.query_end = int( elements[7] )
        self.subject_start = int( elements[8] )
        self.subject_end = int( elements[9] )
        self.e_value = float( elements[10] )
        self.bit_score = float( elements[11] )
        self.__leca_gene = None
        self.__leca_gene_file = None
    
    
    def lookup_leca_gene( self ) -> LecaGene:
        if self.__leca_gene_file != state.leca_file:
            self.__leca_gene_file = state.leca_file
            self.__leca_gene = state.leca_file.lookup_by_leca.get( self.subject_id.lower() ) if state.leca_file else None
            
            if self.__leca_gene is not None and self.__leca_gene.barcode is None:
                self.__leca_gene.barcode = self.barcode
            
            if not self.__leca_gene:
                if not state.leca_file.blast_mismatch_warning:
                    state.leca_file.blast_mismatch_warning = True
                    MCMD.warning( "One or more BLAST genes (e.g. «{}») do not match any gene from the LECA set.".format( self.subject_id ) )
        
        return self.__leca_gene