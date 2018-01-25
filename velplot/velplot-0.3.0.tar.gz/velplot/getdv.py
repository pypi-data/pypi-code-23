import velplot,numpy

def get_dv(dvplot):
    '''
    Calculate central redshift and velocity dispersion.
    '''
    # Calculate mid-redshift among all fitting regions
    if velplot.zmid==None:
        zreg = numpy.empty((0,2))
        for j in range (len(velplot.table1)):
            comment = velplot.comment[j,0].split()
            if 'external' not in comment:
                zmin = float(velplot.table1[j][2])/float(velplot.header[j,1])-1
                zmax = float(velplot.table1[j][3])/float(velplot.header[j,1])-1
            else:
                # Get redshit edges of the external fitting region
                wref = float(atominfo(comment[0])[1])
                wmin = velplot.table1[j][2]
                wmax = velplot.table1[j][3]
                zmin = float(wmin)/wref-1
                zmax = float(wmax)/wref-1
                # Get wavelength edges of the associated tied region
                wref = float(atominfo(comment[2])[1])
                wmin = wref*(zmin+1)
                wmax = wref*(zmax+1)
                # Get redshift edges of the corresponding overlapping region
                wref = float(atominfo(gettrans(comment[2]))[1])
                zmin = float(wmin)/wref-1
                zmax = float(wmax)/wref-1
            zreg = numpy.vstack([zreg,[zmin,zmax]])
        velplot.zmid = (min(zreg[:,0])+max(zreg[:,1]))/2.
    # Calculate maximum velocity dispersions
    dv = 0
    for j in range (len(velplot.header)):
        comment = velplot.comment[j,0].split()
        if 'external' in comment:
            wref  = float(velplot.header[j,1])
            # Wavelength at velplot.zmid in the overlapping region
            reg   = float(atominfo(gettrans(comment[2]))[1])*(velplot.zmid+1)
            # Transition wavelength of the overlapping element
            atom  = float(atominfo(comment[2])[1])
            # Central wavelength of external tied transition for the overlapped system
            wamid = wref*(reg/atom)
            text  = comment[0]+' at z='+str(round(wamid/float(velplot.header[j,1])-1,6))
            dvmin = abs(2*(velplot.table1[j][2]-wamid)/(velplot.table1[j][2]+wamid))*velplot.c
            dvmax = abs(2*(velplot.table1[j][3]-wamid)/(velplot.table1[j][3]+wamid))*velplot.c
            dv    = max(dv,dvmin,dvmax)
        elif 'overlap' in comment:
            wamid = float(velplot.header[j,1])*(velplot.zmid+1)
            text  = comment[2]+' at z='+str(round(wamid/float(atominfo(comment[2])[1])-1,6))
            dvmin = abs(2*(velplot.table1[j][2]-wamid)/(velplot.table1[j][2]+wamid))*velplot.c
            dvmax = abs(2*(velplot.table1[j][3]-wamid)/(velplot.table1[j][3]+wamid))*velplot.c
            dv    = max(dv,dvmin,dvmax)
        else:
            wamid = float(velplot.header[j,1])*(velplot.zmid+1)
            text  = '-'
            dvmin = abs(2*(velplot.table1[j][2]-wamid)/(velplot.table1[j][2]+wamid))*velplot.c
            dvmax = abs(2*(velplot.table1[j][3]-wamid)/(velplot.table1[j][3]+wamid))*velplot.c
            dv    = max(dv,dvmin,dvmax)
        velplot.comment[j,1:] = [text,wamid]
    velplot.dv = dvplot if dvplot!=None else 150 if dv<150 else dv

def get_trans(overlaptrans):
    '''
    Find transition part of overlap system, if existing.
    '''
    for k in range (len(velplot.comment)):
        headline = velplot.comment[k,0].split()
        if 'overlap' in headline and headline[2]==overlaptrans:
            break
    return headline[0]
