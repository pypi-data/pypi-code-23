from enum import Enum
from typing import List
from xml.etree import ElementTree

from cluster_searcher.states import state
from cluster_searcher.constants import COLOURS
from cluster_searcher.confidence import EConfidence, EBlastConfidence
from mhelper import SwitchError


class EResolveColour( Enum ):
    """
    How to colour the output.
    
    :data TEXT:     By text
    :data BLAST:    By BLAST
    :data COMBINED: By text and BLAST
    :data BEST:     A variant of `COMBINED` 
    """
    TEXT = 1
    BLAST = 2
    COMBINED = 3


class ReportGene:
    """
    Genes read from the REPORT file.
    """
    
    
    def __init__( self, gene_name: str, gene_classes: List[str], gene_symbols: List[str], confidence_text: EConfidence, confidence_blast: EBlastConfidence ) -> None:
        self.gene_name = gene_name
        self.gene_symbols = gene_symbols
        self.gene_classes = gene_classes
        self.confidence_text = confidence_text
        self.confidence_blast = confidence_blast
    
    
    def get_colour( self, colour: EResolveColour ):
        if colour == EResolveColour.TEXT:
            return COLOURS.TEXT[self.confidence_text]
        elif colour == EResolveColour.BLAST:
            return COLOURS.BLAST[self.confidence_blast]
        elif colour == EResolveColour.COMBINED:
            return COLOURS.COMBINED[self.confidence_text, self.confidence_blast]
        else:
            raise SwitchError( "colour", colour )


class Report:
    def __init__( self, lines: List[ReportGene] = None ) -> None:
        self.lines: List[ReportGene] = lines or []
    
    
    @staticmethod
    def from_file( read: str ) -> "Report":
        root = None
        
        if read is None:
            if state.last_report_file is not None:
                read = state.last_report_file
            elif state.last_report:
                root = ElementTree.fromstring( state.last_report )
            else:
                raise ValueError( "There is no last report." )
        
        if root is None:
            tree = ElementTree.parse( read )
            root = tree.getroot()
        
        lines: List[ReportGene] = []
        
        for element in root:
            assert element.tag in ("kegg", "gene")
            
            gene_name = element.attrib["name"]
            gene_classes = element.attrib.get( "classes", "old_version" ).split( "," )
            gene_symbols = element.attrib.get( "symbols", "old_version" ).split( "," )
            
            text_confidence = None
            blast_confidence = None
            
            for sub_element in element:
                if sub_element.tag == "text":
                    text_confidence = EConfidence[sub_element.attrib["confidence"]]
                elif sub_element.tag == "blast":
                    blast_confidence = EBlastConfidence[sub_element.attrib["confidence"]]
                else:
                    raise SwitchError( "element.tag", sub_element.tag )
            
            if text_confidence is None or blast_confidence is None:
                raise ValueError( "Missing confidence for «{}».".format( gene_name ) )
            
            lines.append( ReportGene( gene_name, gene_classes, gene_symbols, text_confidence, blast_confidence ) )
        
        return Report( lines )
