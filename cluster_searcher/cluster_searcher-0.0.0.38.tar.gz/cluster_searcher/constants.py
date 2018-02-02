from enum import Enum

from cluster_searcher.confidence import EConfidence, EBlastConfidence
from mhelper import colours


class EOrder( Enum ):
    """
    Colour ordering mode.
    
    :data NORMAL:   Colours are written best-first.
                    KEGG uses the first colour for a class, so this means that classes with more than one gene get
                    the colour of the best-matched gene.
    :data REVERSED: Colours are written best-last.
                    KEGG uses the first colour for a class, so this means that classes with more than one gene get
                    the colour of the least-matched gene.
    """
    NORMAL = 1
    REVERSED = 2


class COLOURS:
    # Colours of the confidence levels:
    # These translate a confidence level into a colour tuple
    # The colour tuple is:  [0]: Priority (if a class contains two genes with different colours either the highest or lowest priority colour will be used, depending on the settings)
    #                       [1]: Text (foreground)
    #                       [2]: Fill (background)
    TEXT = { EConfidence.NAME_EXACT    : (0, colours.BLACK, colours.GREEN),
             EConfidence.NAME_NUMERIC  : (1, colours.BLACK, colours.YELLOW),
             EConfidence.USER_FOUND    : (2, colours.BLACK, colours.DARK_GREEN),
             EConfidence.USER_NOT_FOUND: (3, colours.BLACK, colours.DARK_RED),
             EConfidence.USER_AMBIGUOUS: (4, colours.BLACK, colours.DARK_BLUE),
             EConfidence.USER_DOMAIN   : (5, colours.BLACK, colours.DARK_CYAN),
             EConfidence.TEXT_CONTAINS : (6, colours.BLACK, colours.BLUE),
             EConfidence.NO_MATCH      : (8, colours.BLACK, colours.RED) }
    
    BLAST = { EBlastConfidence.NO_MATCH: (0, colours.BLACK, colours.ORANGE),
              EBlastConfidence.SINGLE  : (1, colours.BLACK, colours.LIME),
              EBlastConfidence.MULTIPLE: (2, colours.BLACK, colours.SPRING_GREEN) }
    
    BLAST_SUCCESS_1A = colours.LIME
    BLAST_SUCCESS_2P = colours.SPRING_GREEN
    BLAST_NO_SUCCESS = colours.RED
    
    TERMS_AMBIGUOUS = colours.GRAY
    TERMS_MATCH = colours.BLACK
    TERMS_MISMATCH = colours.MAGENTA
    
    COMBINED = { (EConfidence.NAME_EXACT, EBlastConfidence.NO_MATCH)    : (0, TERMS_MISMATCH, BLAST_NO_SUCCESS),
                 (EConfidence.NAME_EXACT, EBlastConfidence.SINGLE)      : (1, TERMS_MATCH, BLAST_SUCCESS_1A),
                 (EConfidence.NAME_EXACT, EBlastConfidence.MULTIPLE)    : (2, TERMS_MATCH, BLAST_SUCCESS_2P),
                 (EConfidence.NAME_NUMERIC, EBlastConfidence.NO_MATCH)  : (3, TERMS_AMBIGUOUS, BLAST_NO_SUCCESS),
                 (EConfidence.NAME_NUMERIC, EBlastConfidence.SINGLE)    : (4, TERMS_AMBIGUOUS, BLAST_SUCCESS_1A),
                 (EConfidence.NAME_NUMERIC, EBlastConfidence.MULTIPLE)  : (5, TERMS_AMBIGUOUS, BLAST_SUCCESS_2P),
                 (EConfidence.USER_FOUND, EBlastConfidence.NO_MATCH)    : (6, TERMS_MISMATCH, BLAST_NO_SUCCESS),
                 (EConfidence.USER_FOUND, EBlastConfidence.SINGLE)      : (7, TERMS_MATCH, BLAST_SUCCESS_1A),
                 (EConfidence.USER_FOUND, EBlastConfidence.MULTIPLE)    : (8, TERMS_MATCH, BLAST_SUCCESS_2P),
                 (EConfidence.USER_NOT_FOUND, EBlastConfidence.NO_MATCH): (9, TERMS_MATCH, BLAST_NO_SUCCESS),
                 (EConfidence.USER_NOT_FOUND, EBlastConfidence.SINGLE)  : (10, TERMS_MISMATCH, BLAST_SUCCESS_1A),
                 (EConfidence.USER_NOT_FOUND, EBlastConfidence.MULTIPLE): (11, TERMS_MISMATCH, BLAST_SUCCESS_2P),
                 (EConfidence.USER_AMBIGUOUS, EBlastConfidence.NO_MATCH): (12, TERMS_AMBIGUOUS, BLAST_NO_SUCCESS),
                 (EConfidence.USER_AMBIGUOUS, EBlastConfidence.SINGLE)  : (13, TERMS_AMBIGUOUS, BLAST_SUCCESS_1A),
                 (EConfidence.USER_AMBIGUOUS, EBlastConfidence.MULTIPLE): (14, TERMS_AMBIGUOUS, BLAST_SUCCESS_2P),
                 (EConfidence.USER_DOMAIN, EBlastConfidence.NO_MATCH)   : (15, TERMS_AMBIGUOUS, BLAST_NO_SUCCESS),
                 (EConfidence.USER_DOMAIN, EBlastConfidence.SINGLE)     : (16, TERMS_AMBIGUOUS, BLAST_SUCCESS_1A),
                 (EConfidence.USER_DOMAIN, EBlastConfidence.MULTIPLE)   : (17, TERMS_AMBIGUOUS, BLAST_SUCCESS_2P),
                 (EConfidence.TEXT_CONTAINS, EBlastConfidence.NO_MATCH) : (18, TERMS_AMBIGUOUS, BLAST_NO_SUCCESS),
                 (EConfidence.TEXT_CONTAINS, EBlastConfidence.SINGLE)   : (19, TERMS_AMBIGUOUS, BLAST_SUCCESS_1A),
                 (EConfidence.TEXT_CONTAINS, EBlastConfidence.MULTIPLE) : (20, TERMS_AMBIGUOUS, BLAST_SUCCESS_2P),
                 (EConfidence.NO_MATCH, EBlastConfidence.NO_MATCH)      : (24, TERMS_MATCH, BLAST_NO_SUCCESS),
                 (EConfidence.NO_MATCH, EBlastConfidence.SINGLE)        : (25, TERMS_MISMATCH, BLAST_SUCCESS_1A),
                 (EConfidence.NO_MATCH, EBlastConfidence.MULTIPLE)      : (26, TERMS_MISMATCH, BLAST_SUCCESS_2P) }


class EXT:
    TXT = ".txt"
    KEGG = ".xml"
    LECA = ".txt"
    BLAST = ".tsv"
    REPORT = ".report"
    UDM = ".udm"
    FASTA = ".fasta"