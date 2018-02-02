import hashlib
import urllib.request
from os import path
from typing import Optional, Set, List, Dict, Tuple
from xml.etree import ElementTree

from intermake.engine.environment import MCMD, MENV
from mhelper import ByRef, file_helper, io_helper, array_helper


class KeggClass:
    def __init__( self, id: int, graphics ) -> None:
        assert isinstance( id, int )
        self.index: int = id
        self.genes: "Set[KeggGene]" = set()
        self.unique_gene: Optional[KeggGene] = None
        self.graphics: KeggGraphics = graphics
    
    
    def __str__( self ) -> str:
        return "{}".format( self.index )
    
    
    def complete( self, wrn_unique: ByRef[bool] ) -> bool:
        for gene in self.genes:
            if len( gene.kegg_classes ) == 1:
                self.unique_gene = gene
                gene.unique_class = self
                return True
        
        if not wrn_unique.value:
            wrn_unique.value = True
            MCMD.warning( "There is no gene uniquely identifying one or more KEGG classes (e.g. «{}»).".format( self ) )
        
        return False


class KeggGene:
    """
    Represents a gene (or ortholog) in the KEGG file.
    
    :data gene_ids: KEGG ID(s) for this gene
    :data symbols:  KEGG symbols for this gene
    :data aaseq:    Amino acid sequence for this gene
    """
    
    
    def __init__( self, gene_id: str ):
        """
        CONSTRUCTOR
        See class comments for parameter meanings. 
        """
        self.gene_id: str = gene_id
        self.symbols: Set[str] = set()
        self.aaseq: str = ""
        self.full_info: str = ""
        self.kegg_classes: Set[KeggClass] = set()
        self.kegg_classes_indices: Set[int] = set()
        self.unique_class: Optional[KeggClass] = None
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return self.gene_id


class KeggGraphics:
    def __init__( self, xml ):
        self.name = xml.attrib.get( "name", "" )
        self.fgcolor = xml.attrib.get( "fgcolor", "#000000" )
        self.bgcolor = xml.attrib.get( "bgcolor", "#FFFFFF" )
        self.type = xml.attrib.get( "type", "" )
        self.x = int( xml.attrib.get( "x", "0" ) )
        self.y = int( xml.attrib.get( "y", "0" ) )
        self.width = int( xml.attrib.get( "width", "1" ) )
        self.height = int( xml.attrib.get( "height", "1" ) )
        self.cx = self.x + self.width / 2
        self.cy = self.y + self.height / 2
        self.right = self.x + self.width
        self.bottom = self.y + self.height
        self.left = self.x
        self.top = self.y


class KeggFile:
    """
    Reads and parses the KEGG (KGML) file.
    """
    
    
    def __init__( self, file_name: str, permit: List[str] ) -> None:
        """
        CONSTRUCTOR 
        """
        # Create the container
        self.file_name: str = file_name
        self.genes: List[KeggGene] = []
        self.classes: Set[KeggClass] = set()
        self.all_classes: Set[KeggClass] = set()
        self.empty_classes: Set[KeggClass] = set()
        self.genes_lookup_by_gene_id: Dict[str, KeggGene] = { }
        self.num_genes_rejected: int = 0
        
        # Parse the XML
        tree = ElementTree.parse( file_name )
        root = tree.getroot()
        entries = []
        relations = []
        
        for x in root:
            if x.tag == "entry":
                entries.append( x )
            elif x.tag == "relation":
                relations.append( x )
        
        # Keep track of what we've used
        used_names = set()
        repeated_names = set()
        warn_symbol = False
        warn_aaseq = False
        wrn_unique = ByRef[bool]( False )
        wrn_drop = False
        
        # Cache HTTP records for speed
        cache_folder = MENV.local_data.local_folder( "caches" )
        file_helper.delete_file( path.join( cache_folder, "cached.pickle" ) )  # update old file
        cache_fn = path.join( cache_folder, "cached2.pickle" )
        cached = io_helper.load_binary( cache_fn, { } )
        
        # Iterate over the XML
        for entry in MCMD.iterate( entries, "Resolving names via HTTP" ):
            # Get the gene ID list
            gene_ids = [x for x in entry.attrib["name"].split( " " ) if self.__is_gene_permitted( x, permit )]
            
            graphics = entry.find( "graphics" )
            
            if not gene_ids:
                kegg_class = KeggClass( int( entry.attrib["id"] ), graphics = KeggGraphics( graphics ) )
                self.empty_classes.add( kegg_class )
                self.all_classes.add( kegg_class )
                self.num_genes_rejected += 1
                continue
            
            # Create the class (one class per entry)
            kegg_class = KeggClass( int( entry.attrib["id"] ), graphics = KeggGraphics( graphics ) )
            self.all_classes.add( kegg_class )
            self.classes.add( kegg_class )
            
            # Iterate over genes in the class
            for gene_id in gene_ids:
                # Have we found this gene already?
                kegg_gene = self.genes_lookup_by_gene_id.get( gene_id )
                
                if kegg_gene is not None:
                    kegg_gene.kegg_classes.add( kegg_class )
                    kegg_gene.kegg_classes_indices.add( kegg_class.index )
                    kegg_class.genes.add( kegg_gene )
                    continue
                
                # Create the gene and add to the class
                kegg_gene = KeggGene( gene_id )
                kegg_gene.kegg_classes.add( kegg_class )
                kegg_gene.kegg_classes_indices.add( kegg_class.index )
                kegg_class.genes.add( kegg_gene )
                self.genes.append( kegg_gene )
                self.genes_lookup_by_gene_id[gene_id] = kegg_gene
                
                # Get the data via HTTP
                link = "http://rest.kegg.jp/get/{}".format( gene_id )
                kegg_gene.full_info = self.__get_url( cached, link )
                data_array = kegg_gene.full_info.split( "\n" )
                
                # Get the symbols
                for line in data_array:
                    if line.startswith( "NAME" ):
                        for y in [x.strip() for x in line[4:].split( "," ) if x]:
                            kegg_gene.symbols.add( y )
                
                # Get the AA sequence
                aa_seq = ""
                
                for index, line in enumerate( data_array ):
                    if line.startswith( "AA" ):
                        for i in range( index + 1, len( data_array ) ):
                            if not (data_array[i].startswith( "NT" )):
                                aa_seq += data_array[i]
                            else:
                                break
                
                kegg_gene.aaseq = aa_seq.replace( " ", "" )
                kegg_gene.aaseq_hexdigest = hashlib.sha256( kegg_gene.aaseq.encode( "utf-8" ) ).hexdigest()
                
                # Warnings?
                if not kegg_gene.symbols and not warn_symbol:
                    warn_symbol = True
                    MCMD.warning( "There is at least one gene (e.g. «{}») without at least one symbol.".format( kegg_gene ) )
                
                if not kegg_gene.aaseq and not warn_aaseq:
                    warn_aaseq = True
                    MCMD.warning( "There is at least one gene (e.g. «{}») with no AA sequence.".format( kegg_gene ) )
                
                if kegg_gene.gene_id in used_names:
                    repeated_names.add( kegg_gene.gene_id )
                else:
                    used_names.add( kegg_gene.gene_id )
        
        to_drop = set()
        kegg_classes = list( sorted( self.classes, key = lambda x: x.index ) )
        
        for index, kegg_class in enumerate( kegg_classes ):
            for kegg_class_2 in kegg_classes[index + 1:]:
                if kegg_class.genes == kegg_class_2.genes:
                    if not wrn_drop:
                        wrn_drop = True
                        MCMD.warning( "One or more KEGG classes (e.g. «{}») will be dropped because they are identical to another KEGG class (e.g. «{}»).".format( kegg_class_2, kegg_class ) )
                    
                    to_drop.add( kegg_class_2 )
        
        self.num_classes_dropped = len( to_drop )
        
        for kegg_class in to_drop:
            for kegg_gene in kegg_class.genes:
                kegg_gene.kegg_classes.remove( kegg_class )
            
            self.empty_classes.add( kegg_class )
            self.classes.remove( kegg_class )
        
        kegg_classes = list( sorted( self.classes, key = lambda x: x.index ) )
        
        self.num_classes_not_unique = 0
        
        for kegg_class in kegg_classes:
            if not kegg_class.complete( wrn_unique ):
                self.num_classes_not_unique += 1
        
        # Save the HTTP cache
        io_helper.save_binary( cache_fn, cached )
        
        # Warn about repeated names
        if repeated_names:
            MCMD.warning( "There is at least one gene name (e.g. «{}») that is used by more than one gene. Do not continue. Please change the naming strategy.".format( array_helper.first_or_none( repeated_names ) ) )
        
        self.edges: List[Tuple[str, KeggClass, KeggClass]] = []
        
        for rel in relations:
            e1 = int( rel.attrib["entry1"] )
            e2 = int( rel.attrib["entry2"] )
            ee1 = array_helper.find( self.all_classes, lambda x: x.index == e1, default = None )
            ee2 = array_helper.find( self.all_classes, lambda x: x.index == e2, default = None )
            st = rel.find( "subtype" )
            
            if st is not None:
                name = st.attrib["name"]
            else:
                name = "?"
            
            if not ee1:
                MCMD.warning( "No such ID as {}".format( e1 ) )
                pass
            elif not ee2:
                MCMD.warning( "No such ID as {}".format( e2 ) )
                pass
            else:
                self.edges.append( (name, ee1, ee2) )
        
        if not self.edges:
            MCMD.warning( "No relations?" )
        else:
            MCMD.progress( "{} relations.".format( len( self.edges ) ) )
    
    
    @staticmethod
    def __is_gene_permitted( lst, permitted ) -> bool:
        """
        Obtains if the KEGG type of the entity is permitted.
        For instance we allow orthologies (ko:xxx) to pass, but not compounds (cpd:xxx) or things we don't understand (blah:xxx).
        """
        if permitted is None:
            return True
        
        if " " in lst:
            lst = lst.split( " ", 1 )[0]
        
        if not ":" in lst:
            return False
        
        type_ = lst.split( ":" )[0]
        
        return type_.lower() in permitted
    
    
    @staticmethod
    def __get_url( cached: Dict[str, str], link: str ):
        """
        Gets the URL, from the cache if available.
        """
        result = cached.get( link )
        
        if result is None:
            try:
                result = urllib.request.urlopen( link ).read().decode( "utf-8" )
            except Exception as ex:
                MCMD.warning( "Bad response from «{}»: {}".format( link, ex ) )
                return ""
            
            cached[link] = result
        
        return result
