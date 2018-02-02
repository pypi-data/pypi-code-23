# noinspection PyUnresolvedReferences
import cluster_searcher.report
import cluster_searcher.states
import cluster_searcher.commands as cs


cs.set_cluster( "cluster([0-9]+)(untagged|\.fasta)" )
cs.load_leca( "/Users/martinrusilowicz/mnt/milstore-shared/LECA/conservedclustergeneannotationsfixed.txt" )
cs.load_kegg( "/Users/martinrusilowicz/mnt/milstore-shared/kegg/cell_cycle(hsa04110).xml" )
cs.load_blast( "/Users/martinrusilowicz/mnt/milstore-shared/allgenes.out" )
cs.write_report( silent = True, write = "/Users/martinrusilowicz/tmp/report.report" )
cs.write_udm( colour = cluster_searcher.report.EResolveColour.BLAST )
cs.write_udm( colour = cluster_searcher.report.EResolveColour.COMBINED )
cs.write_udm( colour = cluster_searcher.report.EResolveColour.TEXT )
cs.write_summary()

print( "please confirm the files have been written to «/Users/martinrusilowicz/tmp/» and then delete the files" )
user = input( "confirm: " )

if user.lower() not in ("yes", "y"):
    raise ValueError( "Test failed." )
