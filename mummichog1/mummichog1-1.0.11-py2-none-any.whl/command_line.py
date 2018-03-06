from mummichog1.main import *


def main():

    print fishlogo
    print "mummichog version %s \n" %VERSION
    optdict = dispatcher()
    
    # locate current path, for safe pydata import
    cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
    if cmd_folder not in sys.path: sys.path.insert(0, cmd_folder)
    
    # load specific metabolic model
    if optdict['network'] in ['human', 'hsa', 'Human']:
        import pydata.human_model_humancyc as MetabolicModel
    
    elif optdict['network'] in ['human_mfn', 'hsa_mfn',]:
        import pydata.human_model_mfn as MetabolicModel
        
    elif optdict['network'] in ['mouse', 'Mouse',]:
        import pydata.mouse_model_biocyc as MetabolicModel
        
    elif optdict['network'] in ['fly', 'Fly',]:
        import pydata.fly_model_biocyc as MetabolicModel
        
    elif optdict['network'] in ['yeast', 'Yeast',]:
        import pydata.yeast_model_biocyc as MetabolicModel
        
    else:
        raise KeyError( "Unsupported species/model. Pls contact author." )
        
    
    # prepare output
    os.mkdir(os.path.join(optdict['workdir'], optdict['outdir']))
    
    logging.basicConfig(filename=os.path.join(optdict['workdir'], optdict['outdir'], 'mummichog.log'), 
                        format='%(message)s', 
                        level=logging.INFO)
    logging.info('\n'.join(["mummichog version: %s" %VERSION,
                             "pwd: %s" %os.getcwd(),
                             "user command: %s" %' '.join(sys.argv),
                             "\n",
                             ]))
    
    from functional_analysis import *

    print_and_loginfo("Started @ %s\n" %time.asctime())
    
    HNET = HsaNetwork(MetabolicModel, optdict)
    #
    AC = AnalysisCentral(HNET, HNET.input_mzlist)
    AC.create_dirs()
    AC.run_all_analysis()
    AC.export_csv_data()
    AC.export_sif_related()
    AC.web_export()
    
    
    print_and_loginfo("\nFinished @ %s\n" %time.asctime())


