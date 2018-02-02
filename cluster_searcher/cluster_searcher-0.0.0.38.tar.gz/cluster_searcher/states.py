import re
from typing import List

from cluster_searcher import blast, kegg, leca
from intermake.engine.environment import MENV


class Settings:
    """
    :data last_blast: Last BLAST file loaded
    :data last_leca: Last LECA file loaded
    :data last_kegg: Last KEGG file loaded
    :data last_kegg_permit: Last KEGG permit settings
    """
    
    
    def __init__( self ) -> None:
        self.last_blast = None
        self.last_taxa = None
        self.last_leca = None
        self.last_kegg = None
        self.last_kegg_permit = None


class CsState:
    def __init__( self ):
        self.blast_file: blast.BlastFile = None
        self.leca_file: leca.LecaFile = None
        self.kegg_file: kegg.KeggFile = None
        self.last_report: List[str] = []
        self.last_report_file: str = None
        self.RE_CLUSTER = re.compile( "cluster([0-9]+)(?:untagged|\.fasta)", re.IGNORECASE )
        self.GARBAGE = { "ESP", "universal homolog", "archaeal homolog", "bacterial homolog", "pattern match error" }
        self.settings: Settings = MENV.local_data.store.bind( "settings", Settings() )


state = CsState()
