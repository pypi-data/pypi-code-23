def query():

    import numpy as np
    from hsaquery import query, overlaps
    import os
        
    tab = query.run_query(box=None, proposid=[12471], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G102','G141'], extra=[])
    tab = query.run_query(box=None, proposid=[14594], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G102','G141'], extra=[])
    
    tab = query.run_query(box=None, proposid=[13740], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G102','G141'], extra=[])

    tab = query.run_query(box=None, proposid=[12927], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G102','G141'], extra=[])

    import numpy as np
    from hsaquery import query, overlaps
    import os
    
    tab = query.run_query(box=None, proposid=[14230], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G102','G141'], extra=[])
    
    tabs = overlaps.find_overlaps(tab, buffer_arcmin=1., filters=[], instruments=['WFC3', 'ACS'])

def go_all():
    
    roots = 'j105231+080603 j110326+344948 j112914+095154 j113103-270513 j130033+400907 j131718+392526 j135817+575208 j151005+595848 j151508+213346 j175334+631044 j203924-251434 j222743-270502 j225453+185700 j235536-000300'.split()
    
    roots.extend('j012017+213343 j023507-040202 j051707-441055 j075054+425215 j081331+254507 j101956+274406 j112443-170520 j113007-144930 j143748-014709 j152424+095826 j163429+703133'.split())
    
    # Rigby 14230
    roots = 'j172336+341156 j234028+294745'.split()
    for root in roots:
        go(root=root, maglim=[17,24])
    
    ############### Full archive query
    parent = query.run_query(box=None, proposid=[], instruments=['WFC3'], extensions=['FLT'], filters=['G102', 'G141'], extra=query.DEFAULT_EXTRA+['OBSERVATION.EXPOSURE_DURATION > 260']+["DETECTOR.DETECTOR_NAME LIKE 'IR'"]+['POSITION.FOV_SIZE > 0.04'])
    
    proposals = np.unique(parent['proposal_id'])
    
    tabs = overlaps.find_overlaps(parent, buffer_arcmin=1., filters=[], instruments=['WFC3'], proposid=proposals.tolist(),  extra=query.DEFAULT_EXTRA+['OBSERVATION.EXPOSURE_DURATION > 100']+["DETECTOR.DETECTOR_NAME LIKE 'IR'"])
    
def go(root='j010311+131615', maglim=[17,26]):
    
    import os
    import glob
    import matplotlib.pyplot as plt
    import auto_script
    from imp import reload
    import grizli.prep
    import grizli.utils
    
    roots = [f.split('_info')[0] for f in glob.glob('*dat')]
    HOME_PATH = '/Volumes/Pegasus/Grizli/Automatic'
    
    tab = grizli.utils.GTable.gread(os.path.join(HOME_PATH, '{0}_footprint.fits'.format(root)))
    
    ######################
    ### Download data
    os.chdir(HOME_PATH)
    auto_script.fetch_files(field_root=root, HOME_PATH=HOME_PATH)
    
    if False:
        # Inspect for CR trails
        os.chdir(os.path.join(HOME_PATH, root, 'RAW'))
        os.system("python -c 'from research.grizli.reprocess import inspect; inspect()'")
           
    #######################
    ### Manual alignment
    if False:
        os.chdir(os.path.join(HOME_PATH, root, 'Prep'))
        auto_script.manual_alignment(field_root=root, HOME_PATH=HOME_PATH, skip=True)

    #####################
    ### Alignment & mosaics    
    auto_script.preprocess(field_root=root, HOME_PATH=HOME_PATH, make_combined=False)
        
    # Fine alignment
    stop = False
    out = auto_script.fine_alignment(field_root=root, HOME_PATH=HOME_PATH, min_overlap=0.2, stopme=stop, ref_err=0.08, catalogs=['PS1'], NITER=1, maglim=[17,23], shift_only=True, method='Powell', redrizzle=True)
    plt.close()
    
    # Photometric catalogs
    if not stop:
        tab = auto_script.photutils_catalog(field_root=root)
        auto_script.update_grism_wcs_headers(root)
            
    ######################
    ### Grism prep
    os.chdir(os.path.join(HOME_PATH, root, 'Prep'))
    auto_script.grism_prep(field_root=root)
    
    ######################
    ### Grism extractions
    os.chdir(os.path.join(HOME_PATH, root, 'Extractions'))
    auto_script.extract(field_root=root, maglim=maglim, MW_EBV=tab.meta['MW_EBV'])
    
    ######################
    ### Summary catalog
    os.chdir(os.path.join(HOME_PATH, root, 'Extractions'))
    auto_script.summary_catalog(field_root=root)
    
    