import re
from typing import List, Dict, Set, Tuple, Optional

from cluster_searcher.states import state
from intermake.engine.environment import MCMD
from intermake.engine.theme import Theme


# Regular expressions
_RE_GENE_SYMBOL = re.compile( "gene_symbol:([^ ]+)", re.IGNORECASE )
_RE_DESC = re.compile( "description:([^[]*)", re.IGNORECASE )


class LecaFile:
    """
    Reads and parses the LECA file.
    """
    
    
    def __init__( self, file_name: str ) -> None:
        """
        CONSTRUCTOR
        
        Loads the clusters file
        """
        self.file_name = file_name
        self.blast_mismatch_warning = False
        self.clusters: List[LecaCluster] = []
        self.lookup_by_leca: Dict[str, LecaGene] = { }
        self.num_duplicates = 0
        
        current_cluster = None
        multi_warning = False
        
        with open( file_name, "r" ) as file:
            with MCMD.action( "Loading" ) as action:
                for line in file:
                    line = line.strip()
                    
                    # Feedback to user
                    action.increment( text = "{} clusters and {} genes".format( len( self.clusters ), len( self.lookup_by_leca ) ) )
                    
                    # Ignore garbage lines
                    if not line or line in state.GARBAGE:
                        continue
                    
                    # Is this line a cluster header (otherwise it's a gene)
                    cluster_result = state.RE_CLUSTER.search( line )
                    
                    if cluster_result:
                        # Cluster header line
                        cluster_name = cluster_result.group( 1 )
                        current_cluster = LecaCluster( cluster_name )
                        self.clusters.append( current_cluster )
                    else:
                        # Gene line 
                        if current_cluster is None:
                            MCMD.warning( "Gene rejected because there is no cluster: «{}».".format( line ) )
                            continue
                        
                        # Create gene
                        gene = LecaGene( current_cluster, line )
                        
                        if gene.name in self.lookup_by_leca:
                            # Handle duplicates
                            if gene.text != self.lookup_by_leca[gene.name].text:
                                raise ValueError( "There are two genes with the same name «{}» but they have different content:\n«{}»\n«{}»".format( gene.name, gene.text, self.lookup_by_leca[gene.name].text ) )
                            
                            if not multi_warning:
                                multi_warning = True
                                MCMD.warning( "At least one gene (e.g. «{}») appears in multiple clusters.".format( gene.name ) )
                            
                            gene = self.lookup_by_leca[gene.name]
                            gene.clusters.add( current_cluster )
                            
                            if len( gene.clusters ) == 2:
                                self.num_duplicates += 1
                        
                        else:
                            # Normal case - add to lookup table
                            self.lookup_by_leca[gene.name] = gene
                        
                        # Add to cluster
                        current_cluster.genes.append( gene )
    
    
    def load_taxa( self, file_name ) -> Tuple[int, int]:
        """
        Incorporates taxa data into the clusters.
        """
        # Create the lookup table
        lookup_table = { x.name: x for x in self.clusters }
        
        # Iterate over the file
        has_warned_user = False
        has_warned_user_2 = False
        has_warned_user_3 = False
        has_warned_user_4 = False
        current_cluster = None
        num_clusters = 0
        num_taxa = 0
        
        with open( file_name ) as file_in:
            for line in file_in:
                line = line.strip()
                
                if line.startswith( "/" ):
                    cluster_result = state.RE_CLUSTER.search( line )
                    
                    if cluster_result:
                        # Line is cluster header
                        cluster_name = cluster_result.group( 1 )
                        current_cluster = lookup_table.get( cluster_name )
                        num_clusters += 1
                        
                        if current_cluster.taxa or current_cluster.expected_taxa:
                            raise ValueError( "It looks like something went wrong loading the file. Cluster «{}» is defined more than once.".format( cluster_name ) )
                        
                        if current_cluster is None and not has_warned_user:
                            has_warned_user = True
                            MCMD.warning( "At least one cluster (e.g. «{}») does not exist in the current cluster set.".format( cluster_name ) )
                    else:
                        current_cluster = None
                        
                        if not has_warned_user_2:
                            has_warned_user_2 = True
                            MCMD.warning( "At least one cluster (e.g. «{}») does not match the regex and has been dropped.".format( line ) )
                elif current_cluster:
                    if line[0].isdigit():
                        # Line is number of taxa
                        current_cluster.expected_taxa = int( line )
                    else:
                        # Line is taxon name
                        current_cluster.taxa.add( line )
                        num_taxa += 1
        
        # Check the results for errors
        for cluster in self.clusters:
            if len( cluster.taxa ) != cluster.expected_taxa:
                if not has_warned_user_3:
                    has_warned_user_3 = True
                    MCMD.warning( "It looks like something might have gone wrong loading the file. Expected values do not match, e.g. the number of taxa for cluster «{}» is «{}» («{}») but the file stated «{}» taxa were to be expected.".format( cluster.name, len( cluster.taxa ), cluster.taxa, cluster.expected_taxa ) )
            elif len( cluster.taxa ) > 10:
                if not has_warned_user_4:
                    has_warned_user_4 = True
                    MCMD.warning( "It looks like something might have gone wrong loading the file. The number of taxa for cluster «{}» is «{}», which seems excessive".format( cluster.name, len( cluster.taxa ) ) )
        
        return num_clusters, num_taxa


class LecaGene:
    """
    Represents a gene in the LECA file.
    """
    
    
    def __init__( self, cluster: "LecaCluster", text: str ) -> None:
        """
        Constructor
        :param text: Raw text from the LECA file, representing this gene 
        """
        self.clusters = set()
        self.clusters.add( cluster )
        self.text = text.strip().lower()
        self.name = self.text.split( " ", 1 )[0]
        
        m = _RE_GENE_SYMBOL.search( text )
        
        if m:
            self.gene_symbol = str( m.group( 1 ) ).strip( " ." ).lower()
        else:
            self.gene_symbol = ""
        
        m = _RE_DESC.search( text )
        if m:
            self.description = str( m.group( 1 ) ).strip( " ." ).lower()
        else:
            self.description = ""
        
        self.barcode: Optional[str] = None
    
    
    def removed_text( self, remove: List[str] ):
        text = self.text
        
        if remove:
            for to_remove in remove:
                text = text.lower().replace( to_remove.lower(), "..." )
        
        return text
    
    
    def __str__( self ) -> str:
        return "(LECA)" + Theme.BOLD + (self.gene_symbol or "~{}".format( id( self ) )) + Theme.RESET


class LecaCluster:
    ALL_CLUSTERS: "LecaCluster" = None
    
    
    def __init__( self, name: str ):
        self.name: str = name
        self.genes: List[LecaGene] = []
        self.taxa: Set[str] = set()
        self.expected_taxa = 0
    
    
    @property
    def sort_order( self ) -> int:
        return int( self.name )
    
    
    @property
    def xml( self ) -> str:
        return 'name="{}" num_genes="{}" num_taxa="{}" taxa="{}"'.format( self.name,
                                                                          len( self.genes ),
                                                                          len( self.taxa ),
                                                                          ",".join( sorted( self.taxa ) ) )
    
    
    def __str__( self ) -> str:
        return "{}".format( self.name )


LecaCluster.ALL_CLUSTERS = LecaCluster( "all_clusters" )
