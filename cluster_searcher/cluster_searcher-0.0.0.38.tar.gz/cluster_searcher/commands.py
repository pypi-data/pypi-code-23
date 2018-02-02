import os
import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Set, cast

from cluster_searcher import blast, confidence, constants, file_writing, kegg, leca, report
from cluster_searcher.constants import EXT
from cluster_searcher.report import EResolveColour
from cluster_searcher.states import state
from intermake import MCMD, MENV, command
from intermake.engine.theme import Theme
from mhelper import ByRef, Dirname, Filename, MOptional, SwitchError, ansi, array_helper, file_helper, string_helper


@command()
def write_png( file_name: str ):
    """
    Draws the KGML file using BioPython.
    At the time of writing this isn't very good -- use `write_svg` is a better option.
    
    :param file_name:   File to draw
    """
    from Bio.Graphics import KGML_vis
    from Bio.KEGG.KGML import KGML_parser
    pathway = KGML_parser.read( file_helper.read_all_text( file_name ) )
    kgml_map = KGML_vis.KGMLCanvas( pathway )
    kgml_map.draw( file_name + '_drawing.png' )


@command()
def write_svg( file_name: str, html: bool = False, open: bool = False, report_file: Optional[str] = None, colour: report.EResolveColour = report.EResolveColour.BLAST, order: constants.EOrder = constants.EOrder.NORMAL ):
    """
    Draws a diagram from the currently loaded KEGG pathway.
    
    :param file_name:    File to draw (.svg / .html)
    :param html:         Draw with HTML headers instead of SVG ones
    :param open:         Open file after
    :param report_file:  If you specify a report file, colours are picked from this file.
    :param colour:       Controls colouring, if you specify a report file.
    :param order:        Controls colouring priorities, if you specify a report file.
    """
    r = []
    
    # Colours - clear existing
    override_colour = { }
    
    if report_file:
        for class_ in state.kegg_file.all_classes:
            override_colour[class_] = "#808080", "#C0C0C0"
        
        reports = report.Report.from_file( report_file ).lines
        
        if order == constants.EOrder.NORMAL:
            reports = list( sorted( reports, key = lambda x: x.get_colour( colour )[0] ) )
        elif order == constants.EOrder.REVERSED:
            reports = list( sorted( reports, key = lambda x: -x.get_colour( colour )[0] ) )
        else:
            raise SwitchError( "order", order )
        
        for line in reports:
            colour_ = line.get_colour( colour )
            
            gene = state.kegg_file.genes_lookup_by_gene_id.get( line.gene_name )
            
            if gene is not None:
                for class_ in gene.kegg_classes:
                    override_colour[class_] = colour_[1].html, colour_[2].html
    
    # Constants
    SVG_HEADER = """<defs><marker id="markerCircle" markerWidth="8" markerHeight="8" refX="5" refY="5"><circle cx="5" cy="5" r="3" style="stroke: none; fill:#00C000;"/></marker><marker id="markerArrow" markerWidth="13" markerHeight="13" refX="2" refY="6" orient="auto"><path d="M2,2 L2,11 L10,6 L2,2" style="fill: #00C000;" /></marker></defs>"""
    
    # The order in which the layers go 
    HEADER_1 = 1
    HEADER_2 = 2
    GROUP_BOXES = 3
    LINES = 4
    LINE_TEXT = 5
    GENES = 6
    TEXT = 7
    FOOTER_1 = 8
    
    # Basic header
    if html:
        r.append( (HEADER_1, '<html><body><svg width="2048" height="1536">') )
    else:
        r.append( (HEADER_1, '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="2048" height="1536">') )
    
    # Define our arrowheads
    r.append( (HEADER_2, SVG_HEADER) )
    
    # Draw the relationship lines
    for name, origin, destination in state.kegg_file.edges:
        # Get our graphics
        g1 = origin.graphics
        g2 = destination.graphics
        
        # Make the label upper case
        name = name.upper()
        
        # Try to draw the lines from the box edges, not the centres
        x1, y1, x2, y2 = g1.cx, g1.cy, g2.cx, g2.cy
        
        if g1.right < g2.left:
            x1 = g1.right
            x2 = g2.left - 4
        elif g2.right < g1.left:
            x1 = g1.left
            x2 = g2.right + 4
        
        if g1.bottom < g2.top:
            y1 = g1.bottom
            y2 = g2.top - 4
        elif g2.bottom < g1.top:
            y1 = g1.top
            y2 = g2.bottom + 4
        
        # Position the text in the middle of the line
        tx, ty = (x1 + x2) / 2, (y1 + y2) / 2
        
        # Rotate the text if it looks like it will be a bad fit
        if abs( x1 - x2 ) < 32:
            if abs( y1 - y2 ) > 64:
                t = 'transform="rotate(-90,{},{})"'.format( tx, ty )
            else:
                t = 'transform="rotate(-45,{},{})"'.format( tx, ty )
        else:
            t = ""
        
        # Draw the line
        r.append( (LINES, '<line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:#00C000;stroke-width:1;marker-end:url(#markerArrow);" />'.format( x1, y1, x2, y2 )) )
        
        # Draw the line's label
        r.append( (LINE_TEXT, '<text x="{}" y="{}" style="font-family:Verdana;font-size:6;font-weight:normal;fill:#0000FF;" {}>{}</text>'.format( tx, ty, t, name )) )
    
    # Draw the other boxes
    for entity in state.kegg_file.all_classes:
        # Get our graphics
        g = entity.graphics
        x, y, w, h = g.x, g.y, g.width, g.height
        
        if g.type == "roundrectangle":
            # "roundrectangle" are KEGG titles and stuff...
            layer_priority = GROUP_BOXES
            stroke_dasharray = "1,4"
            stroke_width = 1
            stroke_opacity = 0.1
            stroke_colour = "#FFFFFF"
            fill_colour = "#FFFFFF"
            fill_opacity = .1
            font_weight = "bold"
            font_size = 8
        elif not g.name:
            # Unnamed boxes are just boxes 
            layer_priority = GROUP_BOXES
            stroke_dasharray = "0"
            stroke_width = 2
            stroke_opacity = 0.5
            stroke_colour = "#000000"
            fill_colour = "#FF00FF"
            fill_opacity = 0.2
            font_weight = "normal"
            font_size = 8
            x -= 8
            y -= 16
            w += 16
            h += 16
        else:
            # Everything else is a gene (I think)
            layer_priority = GENES
            stroke_dasharray = "0"
            stroke_width = 2
            stroke_opacity = 1.0
            stroke_colour = g.fgcolor
            fill_colour = g.bgcolor
            fill_opacity = .75
            font_weight = "normal"
            font_size = 8
            
            if entity in override_colour:
                stroke_colour, fill_colour = override_colour[entity]
        
        # Drop multi-titled genes to just the first gene
        name = g.name.split( ",", 1 )[0]
        
        # Make the title entity BIG and top-left
        if name.startswith( "TITLE:" ):
            x = 0
            y = 24
            name = name[6:]
            font_size = 24
        
        # Draw the box
        # - unless it is smaller than 8x8, in which case, don't
        if g.width > 8 and g.height > 8:
            r.append( (layer_priority, '<rect x="{}" y="{}" rx="4" ry="4" width="{}" height="{}" style="fill:{};stroke:{};stroke-width:{};stroke-dasharray:{};fill-opacity:{};stroke-opacity:{};" />'.format( x, y, w, h, fill_colour, stroke_colour, stroke_width, stroke_dasharray, fill_opacity, stroke_opacity )) )
        
        # Draw the name, if it has one
        if name:
            r.append( (TEXT, '<text x="{}" y="{}" style="font-family:Verdana;font-size:{};font-weight:{};fill:{};">{}</text>'.format( x + 8, y + 12, font_size, font_weight, stroke_colour, name )) )
    
    # Add the footer
    if html:
        r.append( (FOOTER_1, '</svg></body></html>') )
    else:
        r.append( (FOOTER_1, '</svg>') )
    
    # Write the file
    file_helper.write_all_text( file_name, "\n".join( l for _, l in sorted( r, key = lambda x: x[0] ) ) )
    
    # Open the file
    if open:
        os.system( "open \"" + file_name + "\"" )


@command()
def load_blast( file_name: MOptional[Filename[EXT.BLAST]] = None ):
    """
    Loads the LECA clusters file.
    
    :param file_name:   File to load, or `None` for the last file.
                        If this is `None` the last file will be loaded.
    """
    if not file_name:
        file_name = state.settings.last_blast
    
    if not file_name:
        raise ValueError( "load_blast: A filename must be specified if there is no recent file." )
    
    state.blast_file = blast.BlastFile( file_name )
    MCMD.print( "{} BLASTs loaded.".format( len( state.blast_file.contents ) ) )
    
    if not state.blast_file.contents:
        raise ValueError( "The BLAST file has been loaded but no entries were found." )
    
    state.settings.last_blast = file_name


@command()
def load_taxa( file_name: MOptional[Filename[EXT.TXT]] = None ) -> None:
    """
    Loads the TAXA file.
    :param file_name:   Taxa file, or `None` for the last loaded file. 
    :return: 
    """
    if not file_name:
        file_name = state.settings.last_taxa
    
    if not file_name:
        raise ValueError( "load_taxa: A filename must be specified if there is no recent file." )
    
    if not state.leca_file:
        raise ValueError( "load_taxa: Refused because the LECA must be loaded first." )
    
    num_clusters, num_taxa = state.leca_file.load_taxa( file_name )
    MCMD.print( "{} taxa loaded into {} clusters.".format( num_taxa, num_clusters ) )
    
    state.settings.last_taxa = file_name


@command()
def load_leca( file_name: MOptional[Filename[EXT.LECA]] = None ):
    """
    Loads the LECA clusters file.
    
    :param file_name:   File to load or `None` for the last file.
                        If this is `None` the last file will be loaded.
    """
    if not file_name:
        file_name = state.settings.last_leca
    
    if not file_name:
        raise ValueError( "load_leca: A filename must be specified if there is no recent file." )
    
    state.leca_file = leca.LecaFile( file_name )
    MCMD.print( "{} clusters and {} genes loaded. {} genes appear in more than one cluster.".format( len( state.leca_file.clusters ),
                                                                                                     len( state.leca_file.lookup_by_leca ),
                                                                                                     state.leca_file.num_duplicates ) )
    
    if not state.leca_file.clusters:
        raise ValueError( "The LECA file has been loaded but no clusters were identified." )
    
    state.settings.last_leca = file_name


@command()
def load_kegg( read: MOptional[Filename[EXT.KEGG]] = None, permit: Optional[List[str]] = None ):
    """
    Loads the KEGG (KGML) file.
    
    :param permit:      List of gene types permitted, e.g. `hsa` for human or `eco` for E-coli.
                        If filename is `None` then, unless specified, the last used `permit` value is used. 
    :param read:   File to load.
                        Obtain this by selecting `download KGML` from a KEGG pathway. The `Reference Pathway (KO)` is recommended.
                        If this is `None` the last file will be loaded.
    """
    if not read:
        read = state.settings.last_kegg
        
        if not permit:
            permit = state.settings.last_kegg_permit
    
    if not read:
        raise ValueError( "load_kegg: A filename must be specified if there is no recent file." )
    
    state.kegg_file = kegg.KeggFile( read, permit )
    msg = "{} genes. {} names. {} sequences. {} genes rejected. {} classes were duplicates. {} classes are non-identifiable."
    MCMD.print( msg.format( len( state.kegg_file.genes ),
                            sum( len( gene.symbols ) for gene in state.kegg_file.genes ),
                            sum( 1 for gene in state.kegg_file.genes if gene.aaseq ),
                            state.kegg_file.num_genes_rejected,
                            state.kegg_file.num_classes_dropped,
                            state.kegg_file.num_classes_not_unique ) )
    
    if not state.kegg_file.genes:
        raise ValueError( "The KEGG file has been loaded but no permissible genes were found." )
    
    state.settings.last_kegg = read
    state.settings.last_kegg_permit = permit


@command()
def write_leca_names( file_name: Filename[EXT.TXT] = "stdout", overwrite: bool = False ) -> None:
    """
    Writes the LECA names to a file
    :param file_name:   File to write to
    :param overwrite:   Overwrite without prompt
    """
    
    overwrite_all = ByRef[bool]( overwrite )
    file_out = file_writing.open_write( file_name, "names", overwrite_all )
    
    try:
        for cluster, leca_genes in state.leca_file.clusters:
            for leca_gene in leca_genes:  # type: leca.LecaGene
                file_out.write( leca_gene.name )
    finally:
        file_out.close()


@command()
def write_fasta( file_name: Filename[EXT.FASTA] = "stdout", overwrite: bool = False ) -> None:
    """
    Writes the FASTA file from the current KEGG pathway.
    :param overwrite:   Overwrite without prompt
    :param file_name:   File to write to. Also accepts:
                        «stdout» - write to STDOUT
                        «.xxx» - use the name of the kegg file, but replace the extension with «.xxx»
                        «.»  - same as «.fasta»  
    """
    overwrite_all = ByRef[bool]( overwrite )
    
    if state.kegg_file is None or not state.kegg_file.genes:
        raise ValueError( "Cannot write FASTA because KEGG has not been loaded." )
    
    if file_name == ".":
        file_name = ".fasta"
    
    if file_name.startswith( "." ):
        file_name = file_helper.replace_extension( state.kegg_file.file_name, file_name )
    
    used_names = set()
    file_out = file_writing.open_write( file_name, "fasta", overwrite_all = overwrite_all )
    good = 0
    bad = 0
    
    try:
        for kegg_gene in MCMD.iterate( state.kegg_file.genes, "Writing genes" ):
            if kegg_gene.aaseq:
                name = kegg_gene.gene_id
                
                if name in used_names:
                    raise ValueError( "Refusing to write the FASTA file because the name «{}» is not unique. Try using a different naming strategy.".format( name ) )
                
                file_out.write( ">{}\n".format( name ) )
                file_out.write( kegg_gene.aaseq )
                file_out.write( "\n" )
                good += 1
            else:
                bad += 1
    finally:
        file_out.close()
    
    MCMD.print( "{} gene-sequences written and empty {} gene-sequences skipped.".format( good, bad ) )


@command()
def write_report( silent: bool = False,
                  using: Optional[str] = None,
                  remove: Optional[List[str]] = None,
                  combine: bool = False,
                  write: MOptional[Filename[EXT.REPORT]] = None,
                  overwrite: bool = False,
                  all: bool = False ):
    """
    Prints the overlap between the loaded KEGG, LECA and BLAST sets.
    
    :param overwrite:       Overwrite files without prompt
    :param using:           Set this to a gene symbol or kegg ID and only that gene will be resolved.
                            Using this option changes the default output filename to stdout.
    :param write:          Output REPORT file.
                            If set, a CLUSTERS file is written.
                            If not set, no CLUSTERS output is written.
                            Accepts `None` (default) and `stdout` as a value.
                            The default is a file is generated adjacent to your KEGG file, when `using` is not set.
                            When `using` is set, the default is `stdout`.
                            Note: The `combine` parameter affects the output.
    :param all:             Set this to `True` and a warning will be generated if the KEGG gene isn't in BLAST
                            (i.e. if you are using all clusters, not just the conserved ones)
    :param silent:          Don't run in interactive mode.
                            If set, no interactive prompts are shown.
                            If not set, interactive prompts are shown for ambiguous results (BLUE).
                            
    :param remove:          Remove this text from search.
                            Use this to ignore phrases which confuse gene names (e.g. "CYCLE" being mistaken for "CYC").
                            In interactive mode these can always be added later.
                            
    :param combine:         Combine clusters.
                            If set, one result per gene is yielded. This also greatly reduces the number of interactive prompts!
                            If not set, one result per gene and cluster is yielded.
    """
    LINE_01_ = '<report version="{}" app_version="{}" kegg_file="{}" leca_file="{}" blast_file="{}">\n'
    LINE_02_ = '    <gene name="{}" symbols="{}" classes="{}" unique="{}" num_organisms="{}" organisms="{}">\n'
    LINE_03_ = '        <warning>!!!NON_UNIQUE_NAME!!!</warning>\n'
    LINE_04_ = '        <text confidence="{}" num_clusters="{}" num_organisms="{}" organisms="{}">\n'
    LINE_05_ = '            <cluster confidence="{}" {} />\n'
    LINE_06_ = '        </text>\n'
    LINE_07_ = '        <blast confidence="{}" num_matched_clusters="{}" num_matched_blasts="{}" num_matched_genes="{}" num_organisms="{}" organisms="{}">\n'
    LINE_08a = '            <cluster num_matched_genes="{}" num_matched_blasts="{}" {}>\n'
    LINE_08b = '                <match name="{}" barcode="{}" />\n'
    LINE_08c = '            </cluster>\n'
    LINE_09_ = '        </blast>\n'
    LINE_010 = '    </gene>\n'
    LINE_011 = '</report>\n'
    
    if state.kegg_file is None:
        raise ValueError( "You must load the KEGG data before calling `write_report`. Status = Not loaded." )
    
    if not state.kegg_file.genes or state.leca_file is None or not state.leca_file.clusters:
        raise ValueError( "You must load the KEGG data before calling `write_report`. Status = Loaded, empty." )
    
    if state.leca_file is None:
        raise ValueError( "You must load the LECA data before calling `write_report`. Status = Not loaded." )
    
    if not state.leca_file.clusters:
        raise ValueError( "You must load the LECA data before calling `write_report`. Status = Loaded, empty." )
    
    if state.blast_file is None:
        raise ValueError( "You must load the BLAST data before calling `write_report`. Status = Not loaded." )
    
    if not state.blast_file.contents:
        raise ValueError( "You must load the BLAST data before calling `write_report`. Status = Loaded, empty." )
    
    # Get the remove list 
    remove = remove if remove is not None else []
    
    # Keep track of interactive settings
    ref_interactive = ByRef[bool]( not silent )
    
    # File handles
    report_file = None
    diagram_file = None
    repeated_names = { }
    
    if write is None:
        write = "default"
    
    if write == "default":
        if using:
            write = "stdout"
        else:
            write = file_helper.replace_extension( state.kegg_file.file_name, ".report" if not combine else ".report_c" )
    
    wrn_mismatch = ByRef[bool]( not all )
    overwrite_all = ByRef[bool]( overwrite )
    
    try:
        #
        # Open files
        #
        
        # - CLUSTERS file
        report_file = file_writing.open_write( write, "report", overwrite_all )
        report_file.write( LINE_01_.format( 3,
                                            MENV.version,
                                            file_helper.get_filename_without_extension( state.kegg_file.file_name ),
                                            file_helper.get_filename_without_extension( state.leca_file.file_name ),
                                            file_helper.get_filename_without_extension( state.blast_file.file_name ) ) )
        
        #
        # Iterate over genes in the KEGG pathway
        #
        kegg_gene = ""
        gene_list = list( x for x in state.kegg_file.genes if not using or using in x.symbols or using == x.gene_id )
        
        for index, kegg_gene in MCMD.enumerate( gene_list, "Exhaustive search", text = lambda x: "{} of {}: {}".format( x, len( state.kegg_file.genes ), str( kegg_gene ) ) ):
            assert isinstance( kegg_gene, kegg.KeggGene )
            
            #
            # Get the confidence level(s) for this gene
            #
            query = confidence.ConfidenceQuery( gene_symbols = kegg_gene.symbols,
                                                ref_interactive = ref_interactive,
                                                remove = remove,
                                                show_leca = False,
                                                show_kegg = False,
                                                by_cluster = not combine )
            
            text_results: Dict[leca.LecaCluster, confidence.EConfidence] = find_confidences( query, "GENE {}/{}".format( index, len( state.kegg_file.genes ) ) )
            blast_results: Dict[leca.LecaCluster, confidence.BlastConfidence] = find_blast_confidences( kegg_gene, wrn_mismatch )
            
            #
            # Get the best confidence level for this gene
            #
            best_text = confidence.EConfidence.NO_MATCH
            
            for confidence_ in text_results.values():
                if confidence_.value > best_text.value:
                    best_text = confidence_
            
            if len( blast_results ) == 0:
                best_blast = confidence.EBlastConfidence.NO_MATCH
            elif len( blast_results ) == 1:
                best_blast = confidence.EBlastConfidence.SINGLE
            else:
                best_blast = confidence.EBlastConfidence.MULTIPLE
            
            #
            # Write the REPORT file
            #
            if write is not None:
                all_organisms = set()
                text_organisms = __get_organisms( text_results )
                blast_organisms = __get_organisms( blast_results )
                all_organisms.update( text_organisms )
                all_organisms.update( blast_organisms )
                
                report_file.write( LINE_02_.format( kegg_gene.gene_id,
                                                    ",".join( kegg_gene.symbols ),
                                                    ",".join( str( x.index ) for x in kegg_gene.kegg_classes ),
                                                    kegg_gene.unique_class.index if kegg_gene.unique_class is not None else "-1",
                                                    len( all_organisms ),
                                                    ",".join( all_organisms ) ) )
                
                # Warning
                if kegg_gene.gene_id in repeated_names:
                    report_file.write( LINE_03_ )
                
                # TEXT
                report_file.write( LINE_04_.format( best_text.name,
                                                    len( text_results ),
                                                    len( text_organisms ),
                                                    ",".join( text_organisms ) ) )
                
                for cluster, confidence_ in sorted( text_results.items(), key = lambda x: int( x[0].sort_order ) ):
                    report_file.write( LINE_05_.format( confidence_.name, cluster.xml ) )
                
                report_file.write( LINE_06_ )
                
                # BLAST
                total_blast_genes = set()
                total_blast_lines = set()
                
                for x in blast_results.values():
                    total_blast_lines.update( x.matches )
                    total_blast_genes.update( x.genes )
                
                report_file.write( LINE_07_.format( best_blast.name,
                                                    len( blast_results ),
                                                    len( total_blast_lines ),
                                                    len( total_blast_genes ),
                                                    len( blast_organisms ),
                                                    ",".join( blast_organisms ) ) )
                
                for cluster, count in sorted( blast_results.items(), key = lambda x: int( x[0].sort_order ) ):
                    report_file.write( LINE_08a.format( len( count.genes ), len( count.matches ), cluster.xml ) )
                    for match in count.matches:  # type: blast.BlastLine
                        report_file.write( LINE_08b.format( match.subject_id, match.barcode if match.barcode else "" ) )
                    
                    report_file.write( LINE_08c )
                
                report_file.write( LINE_09_ )
                
                report_file.write( LINE_010 )
    
    finally:
        if report_file is not None:
            report_file.write( LINE_011 )
            
            if isinstance( report_file, file_writing.StdOutWriter ):
                state.last_report = report_file.lines
                state.last_report_file = None
            else:
                state.last_report = []
                state.last_report_file = write
            
            report_file.close()
        
        if diagram_file is not None:
            diagram_file.close()


def __get_organisms( confidences: Iterable[leca.LecaCluster] ) -> Set[str]:
    organisms = set()
    
    for cluster in confidences:
        for organism in cluster.taxa:
            organisms.add( organism )
    
    return organisms


@command()
def write_all_to_report( directories: List[str], silent: bool = True, combine: bool = False, all: bool = False, overwrite: bool = True ):
    """
    Translates all .xml (kgml) files in the specified directory into .report files.
    **Existing files are overwritten default**
    
    :param directories:   Directory to process. All `.xml` files in this folder are read.
    :param silent:        Passed to `write_report`. Note that the default is different. 
    :param all:           Passed to `write_report`. Note that the default is different.
    :param combine:       Passed to `write_report`.
    :param overwrite:     Passed to `write_report`. Note that the default is different.
    """
    file_names = []
    
    for directory in directories:
        file_names.extend( file_helper.list_dir( directory, ".xml" ) )
    
    for file_name in MCMD.iterate( file_names, "Iterating files" ):
        m = re.search( "\(([a-z]+)[0-9]+\)", file_name )
        
        if m is None:
            continue
        
        kegg_fn = file_name
        report_fn = file_helper.replace_extension( file_name, ".report" )
        
        load_kegg( read = kegg_fn, permit = [m.group( 1 )] )
        write_report( silent = silent, combine = combine, overwrite = overwrite, all = all, write = report_fn )


@command()
def write_all_to_udm( directory: Dirname, overwrite: bool = True ):
    """
    Translates all `.report` files in the specified directory into .udm files.
    **Existing files are overwritten by default**
    
    :param directory:   Directory to process. All `.report` files in this folder are read.
    :param overwrite:   Passed to `write_udm`. Note that the default is different.
    """
    file_names = file_helper.list_dir( directory, ".report" )
    
    for file_name in MCMD.iterate( file_names, "Iterating files" ):
        m = re.search( "\(([a-z]+)[0-9]+\)", file_name )
        
        if m is None:
            continue
        
        report_fn = file_name
        udm1_fn = file_helper.replace_extension( file_name, "-(blast).udm" )
        udm2_fn = file_helper.replace_extension( file_name, "-(combined).udm" )
        udm3_fn = file_helper.replace_extension( file_name, "-(text).udm" )
        write_udm( colour = EResolveColour.BLAST, read = report_fn, overwrite = overwrite, write = udm1_fn )
        write_udm( colour = EResolveColour.COMBINED, read = report_fn, overwrite = overwrite, write = udm2_fn )
        write_udm( colour = EResolveColour.TEXT, read = report_fn, overwrite = overwrite, write = udm3_fn )


@command()
def write_summary( read: MOptional[Filename[EXT.REPORT]] = None, write: MOptional[Filename[EXT.TXT]] = None, overwrite: bool = False ):
    """
    Translates the report to a human-readable file.
    
    :param overwrite:   Overwrite files without asking
    :param write:       Output diagram file.
                        Accepts `stdout` as a value. 
                        If this is `None`, a file is written next to the read file, or the kegg file if the read file is also `None`.

    :param read:        File to read. If `None` uses the last output by `write_report` (assuming that you wrote to stdout).
    """
    overwrite_all = ByRef[bool]( overwrite )
    table = __open_write_translation( read, write, ".description", overwrite_all )
    
    try:
        reports = report.Report.from_file( read )
        
        classes: Dict[str, List[report.ReportGene]] = defaultdict( list )
        
        for gene in reports.lines:
            for kegg_class_name in gene.gene_classes:
                classes[kegg_class_name].append( gene )
        
        table.write( "{} genes and {} classes".format( len( reports.lines ), len( classes ) ) )
        
        for class_name, gene_list in classes.items():
            table.write( "\n\n" )
            
            table.write( "[{}]".format( class_name ) + "\n" )
            
            for gene in gene_list:
                symbol: str = array_helper.first_or_none( gene.gene_symbols )
                table.write( symbol.ljust( 20, " " )
                             + gene.confidence_text.name.ljust( 20 )
                             + gene.confidence_blast.name.ljust( 20 )
                             + "\n" )
    finally:
        table.close()


@command()
def write_udm( colour: report.EResolveColour,
               read: Filename[EXT.REPORT],
               write: MOptional[Filename[EXT.UDM]] = None,
               order: constants.EOrder = constants.EOrder.NORMAL,
               overwrite: bool = False ):
    """
    Translates a report to a KEGG user data mapping file.
    
    :param overwrite:   Overwrite file(s) without asking
    :param order:       Controls colouring of classes (boxes) containing more than one gene.
    :param colour:      How to colour the output.
    :param write:       Output diagram file.
                        If this is none, `stdout` is assumed. 
                        If this is `stdout` - output is written to standard output
    :param read:        File to read.
    :param write:       File to write.
    """
    overwrite_all = ByRef[bool]( overwrite )
    diagram = file_writing.open_write( write, "diagram", overwrite_all )
    
    try:
        reports = report.Report.from_file( read ).lines
        
        if order == constants.EOrder.NORMAL:
            reports = list( sorted( reports, key = lambda x: x.get_colour( colour )[0] ) )
        elif order == constants.EOrder.REVERSED:
            reports = list( sorted( reports, key = lambda x: -x.get_colour( colour )[0] ) )
        else:
            raise SwitchError( "order", order )
        
        for line in reports:
            colour_ = line.get_colour( colour )
            foreground_colour = colour_[1].html
            background_colour = colour_[2].html
            diagram.write( "{}\t{},{}".format( line.gene_name, background_colour, foreground_colour ) )
            diagram.write( "\n" )
    finally:
        diagram.close()


def __open_write_translation( read, write, extension, overwrite_all ) -> Any:
    if write is None:
        if read is None:
            if state.last_report_file is not None:
                read_file = state.last_report_file
            elif state.kegg_file is not None and state.kegg_file.file_name:
                read_file = state.kegg_file.file_name
            else:
                read_file = None
        else:
            read_file = read
        
        if not read_file:
            raise ValueError( "Don't know where to write your output to. No KEGG file, last report file, or explicit output given." )
        
        write = file_helper.replace_extension( read_file, extension )
    
    diagram_file = file_writing.open_write( write, "diagram", overwrite_all )
    
    return diagram_file


def __warn_about_used_values( getter, getter_name, affects, warning: ByRef[bool] ):
    """
    Shows a warning if a KEGG name is already in use.
    :param getter:          How to get the name 
    :param getter_name:     For the error message, the name of the name
    :param affects:         For the error message, what this affects
    :return:                Set of repeated names 
    """
    used_uids = set()
    repeated_uids = set()
    
    for kegg_gene in state.kegg_file.genes:
        if getter( kegg_gene ) in used_uids:
            repeated_uids.add( getter( kegg_gene ) )
        else:
            used_uids.add( getter( kegg_gene ) )
    
    if repeated_uids and not warning.value:
        warning.value = True
        MCMD.warning( "There is at least one {} (e.g. «{}») that is used by more than one gene. This means that these genes cannot be presented in {}.".format( getter_name, array_helper.first_or_none( repeated_uids ), affects ) )
    
    return repeated_uids


def find_blast_confidences( kegg_gene: kegg.KeggGene, wrn_mismatch: ByRef[bool] ) -> Dict[leca.LecaCluster, confidence.BlastConfidence]:
    """
    Finds the BLAST matches.
    
    :param wrn_mismatch:    Interaction setting 
    :param kegg_gene:       Gene to find 
    :return:                Dictionary of cluster names vs number of matches  
    """
    if state.blast_file is None or not state.blast_file.contents:
        return { }
    
    clusters: Dict[leca.LecaCluster, confidence.BlastConfidence] = defaultdict( confidence.BlastConfidence )
    
    blast_lines = state.blast_file.lookup_by_kegg.get( kegg_gene.gene_id )
    
    if blast_lines is not None:
        for blast_line in blast_lines:
            leca_gene = blast_line.lookup_leca_gene()
            
            if leca_gene is None:
                if not wrn_mismatch.value:
                    wrn_mismatch.value = True
                    MCMD.warning( "One or more KEGG genes (e.g. «{}») reference a missing LECA gene (e.g. «{}») via BLAST.".format( kegg_gene, blast_line.subject_id ) )
                
                continue
            
            for cluster in leca_gene.clusters:
                c = clusters[cluster]
                c.matches.append( blast_line )
                c.genes.add( leca_gene )
    
    return clusters


def find_confidences( query: confidence.ConfidenceQuery, title: str ) -> Dict[leca.LecaCluster, confidence.EConfidence]:
    """
    Gets our confidence level that a gene is in the LECA set.
    
    :param title:           Title used for interactive queries 
    :param query:           The query     
    :return:                The confidence level
    """
    results: List[confidence.Result] = _find_all( query )
    lp_results = ByRef[List[confidence.Result]]( results )
    
    if query.by_cluster:
        clusters = set()
        
        for result in results:
            clusters.update( result.leca_gene.clusters )
        
        results_: Dict[leca.LecaCluster, confidence.EConfidence] = { }
        
        for cluster in clusters:
            results_[cluster] = __find_confidence_of_subset( query, lp_results, lambda x: cluster in x.leca_gene.clusters, "{} - CLUSTER {}".format( title, cluster ) )
        
        return results_
    else:
        return { leca.LecaCluster.ALL_CLUSTERS: __find_confidence_of_subset( query, lp_results, None, "{} - ALL_CLUSTERS".format( title ) ) }


def __find_confidence_of_subset( query: confidence.ConfidenceQuery, results: ByRef[List[confidence.Result]], filter, title: str, *, remake = False ) -> confidence.EConfidence:
    if remake:
        results.value = _find_all( query )
    
    if filter:
        subset = [x for x in results.value if filter( x )]
    else:
        subset = results.value
    
    best_result = None
    
    for result in subset:
        if best_result is None or result.confidence.value > best_result.confidence.value:
            best_result = result
    
    if best_result is None:
        return confidence.EConfidence.NO_MATCH
    
    best_subset = [x for x in subset if x.confidence == best_result.confidence]
    
    if query.interactive and cast( int, best_result.confidence.value ) <= confidence.EConfidence.TEXT_CONTAINS.value:
        result = __user_query_confidence_of_subset( best_subset, query, title )
        
        if result is None:
            if query.interactive:
                return __find_confidence_of_subset( query, results, filter, title, remake = True )
            else:
                return best_result.confidence
        else:
            return result
    
    return best_result.confidence


def __user_query_confidence_of_subset( subset: List[confidence.Result], query: confidence.ConfidenceQuery, title: str ):
    """
    Queries a confidence level with the user.
    :param subset: Matches
    :param query:   Query 
    :return: 
    """
    # User responses
    _USER_HELP = "help"
    _USER_LECA_SHOW = "leca.show"
    _USER_LECA_SUMMARISE = "leca.summarise"
    _USER_KEGG_SHOW = "kegg.show"
    _USER_KEGG_SUMMARISE = "kegg.summarise"
    _USER_REMOVE_ONCE = "filter"
    _USER_REMOVE = "remove"
    _USER_STOP = "stop_asking"
    _USER_UNSURE = "unsure"
    _USER_NO = "no"
    _USER_DOMAIN = "domain"
    _USER_YES = "yes"
    
    msg = []
    
    if query.show_kegg:
        for kegg_gene in state.kegg_file.genes:
            if any( gene_symbol in query.gene_symbols for gene_symbol in kegg_gene.symbols ):
                msg.append( "********** KEGG **********" )
                msg.append( string_helper.prefix_lines( kegg_gene.full_info, "KEGG: " ) )
    
    for index, result in enumerate( subset ):
        msg.append( "TARGET {}/{} = ".format( index, len( subset ) ) + __get_leca_ansi( result.leca_gene, query ) )
    
    msg_ = []
    msg_set = set()
    
    msg_.append( "***** UNCERTAIN ABOUT THE FOLLOWING MATCH IN «{}», PLEASE PROVIDE DETAILS *****".format( title ) )
    msg_.append( "SEARCH     = " + (Theme.BORDER + "|" + Theme.RESET).join( (Theme.BOLD + gene_symbol + Theme.RESET) for gene_symbol in query.gene_symbols ) )
    
    for line_ in msg:
        for line in line_.split( "\n" ):
            if not any( x.lower() in line.lower() for x in query.gene_symbols ):
                if query.show_leca:
                    msg_.append( Theme.BORDER + "(X)" + line + Theme.RESET )
            elif line not in msg_set:
                msg_.append( line )
                msg_set.add( line )
            else:
                if query.show_leca:
                    msg_.append( Theme.BORDER + "(^)" + line + Theme.RESET )
    
    while True:
        answer = MCMD.question( message = "\n".join( msg_ ),
                                options = (_USER_YES,
                                           _USER_DOMAIN,
                                           _USER_NO,
                                           _USER_UNSURE,
                                           _USER_STOP,
                                           _USER_REMOVE,
                                           _USER_REMOVE_ONCE,
                                           _USER_KEGG_SUMMARISE if query.show_kegg else _USER_KEGG_SHOW,
                                           _USER_LECA_SUMMARISE if query.show_leca else _USER_LECA_SHOW,
                                           _USER_HELP) )
        
        if answer == _USER_YES:
            return confidence.EConfidence.USER_FOUND
        elif answer == _USER_NO:
            return confidence.EConfidence.USER_NOT_FOUND
        elif answer == _USER_DOMAIN:
            return confidence.EConfidence.USER_DOMAIN
        elif answer == _USER_UNSURE:
            return confidence.EConfidence.USER_AMBIGUOUS
        elif answer == _USER_STOP:
            query.interactive = False
            return None
        elif answer == _USER_HELP:
            MCMD.information( string_helper.highlight_quotes(
                    string_helper.strip_lines( """For this gene:
                                                  ....«yes»            = yes, the gene exists
                                                  ....«domain»         = the domain exists, but not the gene
                                                  ....«no»             = no, the gene doesn't exist
                                                  ....«unsure»         = I'm unsure, mark it as such
                                                  ....«filter»         = I'd like you to remove some specific text from the searches
                                                  
                                                  For all queries in this operation:
                                                  ....«stop_asking»    = Stop asking me these questions and just use the best automated guess*
                                                  ....«remove»         = I'd like you to remove some specific text from the searches
                                                  ....«show.kegg»      = Please provide more/less information about these genes (for KEGG, displays only IDs by default, when on shows everything)
                                                  ....«summarise.kegg» = ^^
                                                  ....«show.leca»      = Please provide more/less information about these genes (for LECA, attempts to summarise by default, when on shows everything)
                                                  ....«summarise.leca» = ^^
                                                  ....«help»           = Show this help message""" ), "«", "»", Theme.BOLD, Theme.RESET ) )
            continue
        elif answer == _USER_LECA_SHOW or answer == _USER_LECA_SUMMARISE:
            query.show_leca = not query.show_leca
            return __user_query_confidence_of_subset( subset, query, title )
        elif answer == _USER_KEGG_SHOW or answer == _USER_KEGG_SUMMARISE:
            query.show_kegg = not query.show_kegg
            return __user_query_confidence_of_subset( subset, query, title )
        elif answer == _USER_REMOVE or answer == _USER_REMOVE_ONCE:
            r_answer = MCMD.question( message = "Enter exact text to remove",
                                      options = ["*"] )
            
            if r_answer:
                if answer == _USER_REMOVE_ONCE:
                    query = query.copy()
                
                query.remove.append( r_answer )
            
            return None
        else:
            raise SwitchError( "answer", answer )


def _find_all( query: confidence.ConfidenceQuery ) -> List[confidence.Result]:
    """
    Find all matches to the specified gene in the LECA file.
    
    :param query:       Query
    """
    results: List[confidence.Result] = []
    
    for gene_symbol in query.gene_symbols:
        gene_symbol = gene_symbol.lower()
        escaped_gene_symbol = re.escape( gene_symbol )
        num_accept = gene_symbol[-1] not in "0123456789"
        escaped_gene_symbol_num = escaped_gene_symbol + "[0-9]+"
        
        #
        # Search over all the clusters
        #
        for leca_cluster in state.leca_file.clusters:
            #
            # Search over all the genes in each cluster
            #
            for leca_gene in leca_cluster.genes:
                leca_text = leca_gene.removed_text( query.remove )
                
                if leca_gene.gene_symbol == gene_symbol:
                    # Exact match
                    r = confidence.Result( gene_symbol, leca_gene, confidence.EConfidence.NAME_EXACT )
                elif num_accept and re.search( escaped_gene_symbol_num, leca_gene.gene_symbol, re.IGNORECASE ):
                    r = confidence.Result( gene_symbol, leca_gene, confidence.EConfidence.NAME_NUMERIC )
                elif re.search( escaped_gene_symbol, leca_text, re.IGNORECASE ):
                    r = confidence.Result( gene_symbol, leca_gene, confidence.EConfidence.TEXT_CONTAINS )
                else:
                    r = None
                
                if r is not None:
                    results.append( r )
    
    return results


@command()
def find_text( text: str, regex: bool = False, remove: List[str] = None ):
    """
    Finds text in the loaded file
    
    :param remove:  Don't include this text
    :param text:    Text to find 
    :param regex:   Use regex? 
    """
    
    colour = Theme.VALUE
    normal = Theme.RESET
    
    if not regex:
        text = re.escape( text )
    
    text_regex = re.compile( text, re.IGNORECASE )
    
    for leca_cluster in state.leca_file.clusters:
        printed = False
        
        for gene in leca_cluster.genes:
            line = gene.removed_text( remove )
            text_result = text_regex.search( line )
            
            if text_result:
                s = text_result.start( 0 )
                e = text_result.end( 0 )
                
                if not printed:
                    MCMD.print( "\n" + Theme.TITLE + "CLUSTER " + leca_cluster.name + Theme.RESET )
                    printed = True
                
                MCMD.print( line[:s] + colour + line[s:e] + normal + line[e:] )


@command()
def write_legend( colour: report.EResolveColour ):
    """
    Prints the legend.
    
    :param colour: Colour to get legend for
    """
    if colour == report.EResolveColour.BLAST:
        mode = constants.COLOURS.BLAST
    elif colour == report.EResolveColour.TEXT:
        mode = constants.COLOURS.TEXT
    elif colour == report.EResolveColour.COMBINED:
        mode = constants.COLOURS.COMBINED
    elif colour == report.EResolveColour.NONE:
        return
    else:
        raise SwitchError( "colour", colour )
    
    for key, value in mode.items():
        if isinstance( key, tuple ):
            key_name = key[0].name + " + " + key[1].name
        else:
            key_name = key.name
        
        _, fore, back = value
        
        MCMD.print( "{}{}{}{}".format( ansi.back( back.r, back.g, back.b ),
                                       ansi.fore( fore.r, fore.g, fore.b ),
                                       string_helper.centre_align( key_name, 40 ),
                                       ansi.RESET ) )


@command()
def find_gene( text: List[str], remove: List[str], silent: bool = False, combine: bool = False ):
    """
    Finds a specific gene in the loaded file
    
    :param text:    Gene name or aliases to find 
    :param silent:  Don't run in interactive mode
    :param remove:  Remove this text from search
    :param combine: Combine clusters (yields one result per gene)
    """
    lecas = set()
    
    ref_interactive = ByRef[bool]( not silent )
    
    query = confidence.ConfidenceQuery( gene_symbols = text,
                                        ref_interactive = ref_interactive,
                                        remove = remove,
                                        show_kegg = False,
                                        show_leca = False,
                                        by_cluster = not combine )
    
    for r in _find_all( query ):
        MCMD.print( str( r ) )
        lecas.add( r.leca_gene )
    
    for leca in lecas:
        leca_text = __get_leca_ansi( leca, query )
        MCMD.print( leca_text )


def __get_leca_ansi( leca: leca.LecaGene, query: confidence.ConfidenceQuery ):
    """
    Formats a LECA gene for the ANSI console.
    :param leca:    The gene 
    :param query:   The query 
    :return:        ANSI text 
    """
    leca_text = leca.removed_text( query.remove )
    leca_text = string_helper.highlight_regex( leca_text, " [a-zA-Z_]+:", "\n" + Theme.COMMAND_NAME, Theme.RESET, group = 0 )
    
    for gene_symbol in query.gene_symbols:
        leca_text = string_helper.highlight_regex( leca_text, re.escape( gene_symbol ), Theme.BOLD_EXTRA, Theme.RESET, group = 0 )
    
    return leca_text


@command()
def set_cluster( new_regex: Optional[str] = None ):
    """
    View of modifies the cluster regex in the LECA file.
    :param new_regex:   New regex to use. Leave blank to display the current regex.
    """
    if new_regex:
        state.RE_CLUSTER = re.compile( new_regex, re.IGNORECASE )
    
    MCMD.print( state.RE_CLUSTER.pattern )


@command()
def set_garbage( add: Optional[List[str]] = None, remove: Optional[List[str]] = None, clear: bool = False ):
    """
    Adds, removes or views garbage elements.
    :param clear:   Clear all garbage elements
    :param add:     Element(s) to add 
    :param remove:  Element(s) to remove
    :return: 
    """
    if clear:
        state.GARBAGE.clear()
    
    if add:
        for x in add:
            state.GARBAGE.add( x )
    
    if remove:
        for x in remove:
            state.GARBAGE.remove( x )
    
    MCMD.print( ", ".join( state.GARBAGE ) )
