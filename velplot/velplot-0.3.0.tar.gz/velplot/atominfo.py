import velplot,numpy

def isfloat(value):
    """
    Check if given value is of float type or not

    Parameters
    ----------
    value : str
      Value to be checked.
    """
    try:
      float(value)
      return True
    except ValueError:
      return False

def atom_list(atompath):     # Store data from atom.dat
    """
    Create list of atomic data based on input atom.dat

    Parameters
    ----------
    atompath : str
      Full path to the atom.dat
    """
    atom = numpy.empty((0,6))
    atomdat = numpy.loadtxt(atompath,dtype='str',delimiter='\n')
    for element in atomdat:
        l       = element.split()
        i       = 0      if len(l[0])>1 else 1
        species = l[0]   if len(l[0])>1 else l[0]+l[1]
        wave    = 0 if len(l)<i+2 else 0 if isfloat(l[i+1])==False else l[i+1]
        f       = 0 if len(l)<i+3 else 0 if isfloat(l[i+2])==False else l[i+2]
        gamma   = 0 if len(l)<i+4 else 0 if isfloat(l[i+3])==False else l[i+3]
        mass    = 0 if len(l)<i+5 else 0 if isfloat(l[i+4])==False else l[i+4]
        alpha   = 0 if len(l)<i+6 else 0 if isfloat(l[i+5])==False else l[i+5]
        if species not in ['>>','<<','<>','__']:
            atom = numpy.vstack((atom,[species,wave,f,gamma,mass,alpha]))
    return atom

def atom_info(atomID):
    '''
    Get atomic data from selected atomID
    '''
    target = [0,0,0,0,0]
    atomID = atomID.split('_')
    imet   = numpy.where(velplot.atom[:,0]==atomID[0])[0]
    wmet   = [abs(float(velplot.atom[i,1])-float(atomID[1])) for i in imet]
    if len(wmet)==0:
        print '\nERROR: Transition not found, check that the transition ID'
        print '       is specified in the fort file, or that the ID list'
        print '       is called using the --header argument.\n'
        quit()
    iref = imet[wmet.index(min(wmet))]
    wref = float(velplot.atom[iref,1])
    for i in imet:
        element    = velplot.atom[i,0]
        wavelength = velplot.atom[i,1]
        oscillator = velplot.atom[i,2]
        gammavalue = velplot.atom[i,3]
        qcoeff     = velplot.atom[i,5]
        cond1      = abs( float(wavelength) - wref ) < 0.1
        cond2      = float(oscillator) > float(target[2])
        if cond1 and cond2:
            target = [element,wavelength,oscillator,gammavalue,qcoeff]
    return target

def atom_mass(species):
    '''
    Store ion mass extracted from atom.dat
    '''
    mass = None
    for i in range(len(velplot.masslist)):
        for j in velplot.ionlevel:
            if species==velplot.masslist[i,0]+j:
                mass = velplot.masslist[i,1]
    if mass==None:
        print 'Atomic mass not found for',species
        quit()
    return mass
