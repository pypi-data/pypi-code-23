from enum import Enum
from typing import List, Set, Iterable, Optional

from cluster_searcher.blast import BlastLine
from cluster_searcher.leca import LecaGene
from intermake.engine.theme import Theme
from mhelper import ByRef


class EConfidence( Enum ):
    """
    Confidence level of the match.
    
    The target set comprises all LECA genes (when the `combine` flag is set) or a cluster of LECA genes (when the `combine` flag is not set).
    
    See the `COLOURS` field for the corresponding colours.
    
    :data NO_MATCH:         Level 1. Gene not found in the target set
    :data ERROR:            Level 2. Gene found or not found, we can't report because the gene does not possess a viable UID.
    :data TEXT_CONTAINS:    Level 3. Gene found in the text of a gene of the target set.
    :data NAME_NUMERIC:     Level 4. Gene found in the name of a a gene in the target set, but suffixed with a number. The gene name itself does not end with a number.
    :data USER_NOT_FOUND:   Level 5. User reported gene as not found ("no").
    :data USER_FOUND:       Level 6. User reported gene as found ("yes")
    :data USER_AMBIGUOUS:   Level 7. User reported gene as ambiguous ("unsure")
    :data USER_DOMAIN:      Level 8. User reported gene domain as present ("domain")
    :data NAME_EXACT:       Level 9. Exact gene name found.
    """
    NO_MATCH = 1
    TEXT_CONTAINS = 3
    NAME_NUMERIC = 4
    USER_NOT_FOUND = 5
    USER_FOUND = 6
    USER_AMBIGUOUS = 7
    USER_DOMAIN = 8
    NAME_EXACT = 9


class EBlastConfidence( Enum ):
    """
    Confidence level of a BLAST match.
    
    See the `COLOURS` field for the corresponding colours.
    
    :data NO_MATCH:     No BLAST match
    :data SINGLE:       One cluster OR the `combine` flag is set
    :data MULTIPLE:     Multiple clusters (not applicable when the `combine` flag is set)
    """
    NO_MATCH = 0
    SINGLE = 1
    MULTIPLE = 2


class Result:
    """
    Represents a LECA-KEGG gene match.
    """
    
    
    def __init__( self, symbol: str, leca_gene: LecaGene, confidence: EConfidence ):
        """
        CONSTRUCTOR
        :param symbol:          Symbol the match was made under 
        :param leca_gene:       Matching gene in the LECA set 
        :param confidence:      Confidence of the match 
        """
        self.gene_symbol = symbol
        self.leca_gene = leca_gene
        self.confidence = confidence
    
    
    def __repr__( self ) -> str:
        return "{} ({}) {}".format( self.leca_gene, Theme.COMMENT + str( self.confidence ) + Theme.RESET, Theme.BOLD + str( self.gene_symbol ) + Theme.RESET )


class BlastConfidence:
    def __init__( self ) -> None:
        self.matches: List[BlastLine] = list()
        self.genes: Set[LecaGene] = set()


class ConfidenceQuery:
    """
    :data gene_symbols:    Aliases for this gene 
    :data interactive:     Permit interactive searching 
    :data remove:          Exclude these text literals when searching descriptions 
    :data verbose:         Provide more information when interactively searching
    """
    
    
    def __init__( self, *, gene_symbols: Iterable[str], ref_interactive: ByRef[bool], remove: Optional[List[str]], show_leca: bool, show_kegg: bool, by_cluster: bool ):
        self.gene_symbols = gene_symbols
        self.__interactive = ref_interactive
        self.remove = remove if remove is not None else []
        self.show_leca = show_leca
        self.show_kegg = show_kegg
        self.by_cluster = by_cluster
    
    
    @property
    def interactive( self ) -> bool:
        return self.__interactive.value
    
    
    @interactive.setter
    def interactive( self, value: bool ):
        self.__interactive.value = value
    
    
    def copy( self ) -> "ConfidenceQuery":
        return ConfidenceQuery( gene_symbols = list( self.gene_symbols ), ref_interactive = self.__interactive, remove = list( self.remove ), show_leca = self.show_leca, show_kegg = self.show_kegg, by_cluster = self.by_cluster )