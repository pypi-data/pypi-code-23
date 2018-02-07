def testing():
    import numpy as np
    import matplotlib.pyplot as plt
    from hsaquery import query
    
    # Query around GN-z11 program
    tab = query.run_query(box=None, proposid=[13871], instruments=['WFC3', 'ACS'], filters=[])
    tab['orientat'] = [query.get_orientat(p) for p in tab['footprint']]
    
    # Search imaging around the center
    box = [np.median(tab['ra']), np.median(tab['dec']), 12]
        
    filters = ['G102', 'F140W', 'F775W']
    #filters = ['F140W']
    extras = query.run_query(box=box, proposid=[], instruments=['WFC3', 'ACS'], filters=filters, extra=[])
    
    fig = plt.figure(figsize=[12,3.5])
    ax = fig.add_subplot(141)
    query.show_footprints(tab, ax=ax)
    ax.set_title('13871')
    
    for i, filt in enumerate(filters):
        print(filt)    
        ax = fig.add_subplot(142+i)
        query.show_footprints(extras[extras['filter'] == filt], ax=ax)
        ax.set_title(filt)
    
    for ax in fig.axes:        
        ax.set_xlim(189.46939409999999, 188.89701790000001)
        ax.set_ylim(62.078094353454389, 62.402351754992722)
        ax.grid()
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    
    fig.tight_layout(pad=0.2)
    #fig.savefig('hsaquery_demo.png')
    
    # Bielby
    tab = query.run_query(box=None, proposid=[14594], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G141'])
    
    tab = query.run_query(box=None, proposid=[12177], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G141'])
    targets = np.unique(tab['target'])
    
    # WISP
    tab = query.run_query(box=None, proposid=[14178], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G102','G141'])
    targets = np.unique(tab['jtargname'])
    
    # Stanford
    tab = query.run_query(box=None, proposid=[11597,12203], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=['G102','G141'], extra=[])
    targets = np.unique(tab['target'])
    targets = np.unique(tab['jtargname'])
    
    for target in targets:
        print(target)
        m = tab['jtargname'] == target
        m = tab['target'] == target
        box = [np.median(tab['ra'][m]), np.median(tab['dec'][m]), 10]
        xtab = query.run_query(box=box, proposid=[], instruments=['WFC3', 'ACS'], extensions=['FLT'], filters=[], extra=[])
        
        fig = plt.figure(figsize=[5,5])
        ax = fig.add_subplot(111)
        query.show_footprints(tab[m], ax=ax)
        query.show_footprints(xtab, ax=ax)
        ax.set_title(target)
        ax.grid()
        fig.tight_layout(pad=0.1)
        
        fig.savefig('{0}_footprint.png'.format(target))
        
    ###### Polygon matches
    from hsaquery.query import parse_polygons
    from shapely.geometry import Polygon
    from descartes import PolygonPatch

    polygons = []
    for i in range(len(tab)):
        poly = parse_polygons(tab['footprint'][i])#[0]
        pshape = [Polygon(p) for p in poly]
        for i in range(1,len(poly)):
            pshape[0] = pshape[0].union(pshape[i])
        
        polygons.append(pshape[0].buffer(1./60))
    
    match_poly = [polygons[0]]
    match_ids = [[0]]
    
    for i in range(1,len(tab)):
        print(i)
        has_match = False
        for j in range(len(match_poly)):
            isect = match_poly[j].intersection(polygons[i])
            #print(tab['target'][i], i, isect.area > 0)
            if isect.area > 0:
                match_poly[j] = match_poly[j].union(polygons[i])
                match_ids[j].append(i)
                has_match = True
                continue
                
        if not has_match:
            match_poly.append(polygons[i])
            match_ids.append([i])
    
    BLUE = '#6699cc'
    for i in range(len(match_poly)):
        #i+=1
        p = match_poly[i]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        idx = np.array(match_ids[i])
        query.show_footprints(tab[idx], ax=ax)

        box = [np.mean(tab['ra'][idx]), np.mean(tab['dec'][idx]), 6]
        
        jname = query.radec_to_targname(box[0], box[1], scl=1000)
        print('\n\n', i, jname, box[0], box[1])
        ax.scatter(box[0], box[1], marker='+', color='k')
        
        xtab = query.run_query(box=box, proposid=[], instruments=['WFC3', 'ACS'], extensions=['FLT','C1M'], filters=[], extra=["TARGET.TARGET_NAME NOT LIKE '{0}'".format(calib) for calib in ['DARK','EARTH-CALIB', 'TUNGSTEN', 'BIAS', 'DARK-EARTH-CALIB', 'DARK-NM', 'DEUTERIUM']])
        
        pointing_overlaps = np.zeros(len(xtab), dtype=bool)
        for j in range(len(xtab)):
            poly = parse_polygons(xtab['footprint'][j])#[0]
            pshape = [Polygon(p) for p in poly]
            for k in range(1,len(poly)):
                pshape[0] = pshape[0].union(pshape[k])
            
            isect = p.intersection(pshape[0])
            pointing_overlaps[j] = isect.area > 0
            
        xtab = xtab[pointing_overlaps]
        filter_target = np.array(['{0} {1}'.format(xtab['instdet'][i], xtab['filter'][i]) for i in range(pointing_overlaps.sum())])
        print(np.unique(xtab['target']), '\n')
        for filt in np.unique(filter_target):
            mf = filter_target == filt
            print('    {0:20s}  {1:3d}  {2:>8.1f}'.format(filt, mf.sum(), xtab['exptime'][mf].sum()))
            
        query.show_footprints(xtab, ax=ax)
        
        patch1 = PolygonPatch(p, fc=BLUE, ec=BLUE, alpha=0.1, zorder=2)
        
        xy = p.boundary.xy
        ax.plot(xy[0], xy[1])
        ax.add_patch(patch1)
        
        ax.grid()
        
        # Resize
        xr, yr = ax.get_xlim(), ax.get_ylim()
        dx = (xr[1]-xr[0])*np.cos(yr[0]/180*np.pi)*60
        dy = (yr[1]-yr[0])*60
        ax.set_title(jname)
        fig.set_size_inches(5,5*dy/dx)
        fig.tight_layout(pad=0.5)
        fig.savefig('{0}_footprint.pdf'.format(jname))
        
        xtab.write('{0}_footprint.fits'.format(jname), format='fits', overwrite=True)
        
        plt.close()
        
def test_query():
    
    from hsaquery import query, fetch
    
    box = [20.0860779,	21.5608514, 3]
    tab = query.run_query(box=box, proposid=[], instruments=['ACS','WFC3','WFPC2'], filters=[], extensions=['C1M','RAW'], extra=[])
    curl = fetch.make_curl_script(tab)
    
    