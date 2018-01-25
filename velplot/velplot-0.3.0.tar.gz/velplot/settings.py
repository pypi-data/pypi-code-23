""" Loading module and variables """

import sys,os,numpy
from matplotlib import rc
from datetime import datetime

def show_help():
    '''
    Help menu to be printed on demand.
    '''
    print ""
    print "-------------------------------------------------------------------"
    print "  Velocity plot software"
    print "-------------------------------------------------------------------"
    print ""
    print "usage: velplot <fortfile> [--args]" 
    print ""
    print "optional arguments: "
    print "   --atomdir       Path to a custom atom.dat"
    print "                     (default: in current repository)"
    print "   --details       Plot individual Voigt profiles"
    print "   --dispersion    Spectral velocity dispersion for high-resolution"
    print "                   individual Voigt profiles"
    print "                     (default: 0.01 km/s)"
    print "   --dv            Custom velocity range for plotting"
    print "   --extra         Add vertical line to identify specific region."
    print "                     Multiple velocities can be specified by using"
    print "                     the colon symbol (:) to separate the values"
    print "   --fit           Run VPFIT and embed final results in fort.13"
    print "   --getwave       Get wavelength array from the spectrum"
    print "   --header        List of transition IDs of each fitting region"
    print "                     (default: embedded in the fort file)"
    print "   --nores         Do not plot the residuals"
    print "   --output        Give custom output filename"
    print "                     (default: date-time in yyyymmdd-HHMMSS format)"
    print "   --unscale       Don't correct the data and distort the models"
    print "   --version       Path to a custom vpfit executable"
    print "                     (default: vpfit)"
    print "   --vpfsetup      Path to a custom vp_setup.dat"
    print "                     9default: in current repository)"
    print "   --zmid          Central redshift to plot transitions"
    print ""
    print "-------------------------------------------------------------------"
    print ""
    quit()

rc('font', size=2, family='serif')
rc('axes', labelsize=2, linewidth=0.2)
rc('legend', fontsize=2, handlelength=10)
rc('xtick', labelsize=8)
rc('ytick', labelsize=8)
rc('lines', lw=0.2, mew=0.2)
rc('grid', linewidth=0.2)
k = 1.3806488*10**-23    # m^2.kg.s^-2.K^-1
c = 299792.458           # km/s
ionlevel = ['I','II','III','IV','V','VI','VII','VIII','IX','X']
masslist = numpy.array([['Al',26.981539],
                     ['Ar',39.948000],
                     ['Be', 9.012182],
                     ['C' ,12.010700],
                     ['Ca',40.078000],
                     ['Cl',35.453000],
                     ['Cr',51.996100],
                     ['Cu',63.546000],
                     ['D' , 2.014102],
                     ['Fe',55.845000],
                     ['Ga',69.723000],
                     ['Ge',72.640000],
                     ['H' , 1.007940],
                     ['He', 4.002602],
                     ['O' ,15.999400],
                     ['Mg',24.305000],
                     ['Aw',24.305000], # Duplicate of Mg used in isotope analysis
                     ['Mn',54.938045],
                     ['N' ,14.006700],
                     ['Na',22.989769],
                     ['Ne',20.179700],
                     ['Ni',58.693400],
                     ['P' ,30.973762],
                     ['S' ,32.065000],
                     ['Si',28.085500],
                     ['Ti',47.867000],
                     ['Zn',65.380000]],dtype=object)

argument   = numpy.array(sys.argv, dtype='str')
fortfile   = None if len(sys.argv)==1 else str(sys.argv[1])
details    = '--details' in sys.argv
error      = '--error'   in sys.argv
fit        = '--fit'     in sys.argv
getwave    = '--getwave' in sys.argv
illcond    = '--illcond' in sys.argv
nores      = '--nores'   in sys.argv
show       = '--show'    in sys.argv
unscale    = '--unscale' in sys.argv
dispersion = 0.01     if '--dispersion' not in sys.argv else float(argument[numpy.where(argument=='--dispersion')[0][0]+1])
dv         = None     if '--dv'         not in sys.argv else float(argument[numpy.where(argument=='--dv')[0][0]+1])
zmid       = None     if '--zmid'       not in sys.argv else float(argument[numpy.where(argument=='--zmid')[0][0]+1])
extra      = None     if '--extra'      not in sys.argv else   str(argument[numpy.where(argument=='--extra')[0][0]+1])
header     = 'infort' if '--header'     not in sys.argv else   str(argument[numpy.where(argument=='--header')[0][0]+1])
version    = 'vpfit'  if '--version'    not in sys.argv else   str(argument[numpy.where(argument=='--version')[0][0]+1])
atom       = './atom.dat'     if '--atom'     not in sys.argv else str(argument[numpy.where(argument=='--atom')[0][0]+1])
vpfsetup   = './vp_setup.dat' if '--vpfsetup' not in sys.argv else str(argument[numpy.where(argument=='--vpfsetup')[0][0]+1])
output     = (datetime.now()).strftime('%y%m%d-%H%M%S') if '--output' not in sys.argv else argument[numpy.where(argument=='--output')[0][0]+1]
