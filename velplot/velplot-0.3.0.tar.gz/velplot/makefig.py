#!/usr/bin/env python
import velplot,os,sys,numpy,seaborn
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def make_figure(atom=velplot.atom,details=velplot.details,dispersion=velplot.dispersion,
                dvplot=velplot.dv,error=velplot.error,extra=velplot.extra,fit=velplot.fit,
                getwave=velplot.getwave,fortfile=velplot.fortfile,header=velplot.header,
                illcond=velplot.illcond,nores=velplot.nores,output=velplot.output,
                show=velplot.show,unscale=velplot.unscale,version=velplot.version,
                vpfsetup=velplot.vpfsetup,zmid=velplot.zmid):
    '''
    Main function to create velocity plot.

    Parameters
    ----------
    atom : str
      Path to a custom atom.dat
    details : bool
      Plot individual Voigt profiles
    dispersion : float
      Spectral velocity dispersion for high-resolution individual Voigt profiles
    dv : float
      Custom velocity range for plotting
    extra : str
      Add vertical line to identify specific region. Multiple velocities
      can be specified by using the colon symbol (:) to separate the values.
    fit : bool
      Run VPFIT and embed final results in fort.13
    error : bool
      Run VPFIT only once to get error estimates
    getwave : bool
      Get wavelength array from the spectrum
    fortfile : str
      fort.13 file to be read
    header : str
      List of transition IDs of each fitting region
    illcond : bool
      Run VPFIT with ill-conditioning
    nores : bool
      Do no plot the residuals
    output : str
      Give custom output filename
    show : bool
      Flag whether the figure is shown using Python interface.
    unscale : bool
      Don't correct the data and distort the models
    version : str
      Path to a custom vpfit executable
    vpfsetup : str
      Path to a custom vp_setup.dat
    zmid : float
      Central redshift to plot transitions

    Examples
    --------
    As executables:

    >>> velplot fort.13 --output turbulent --version vpfit10 --header header.dat

    As Python script:

    >>> import velplot
    >>> velplot.make_figure(fortfile='fort.13',header='header.dat',show=True,details=True,getwave=True)
    '''
    # Set up header file
    velplot.headlist = numpy.loadtxt(header,dtype='str',comments='!',delimiter='\n',ndmin=1)
    # Set up atomic transition list
    os.environ['ATOMDIR'] = atom
    if os.path.exists(atom):
        velplot.atom = velplot.atom_list(atom)
    else:
        print 'ERROR: atom.dat not found...'
        quit()
    # Set up VPFIT settings
    os.environ['VPFSETUP'] = vpfsetup
    if os.path.exists(vpfsetup)==True:
        pcvals,lastchtied,daoaun = False,'z',1
        for line in numpy.loadtxt(vpfsetup,dtype='str',delimiter='\n'):
            if 'pcvals' in line and line.split()[0][0]!='!':
                pcvals = True
            if 'lastchtied' in line and line.split()[0][0]!='!':
                lastchtied = line.split()[1].lower()
            if 'daoaun' in line and line.split()[0][0]!='!':
                daoaun = float(line.split()[1])
    else:
        print 'ERROR: vp_setup.dat not found...'
        quit()
    # Remove previously created chunks
    if os.path.exists('./chunks/')==True:
        os.system('rm -rf chunks/')
    if fit or error or illcond:
        velplot.fit_fort(fortfile)
        os.system('mv fort.18 '+fortfile.replace('.13','.18'))
        os.system('mv fort.26 '+fortfile.replace('.13','.26'))
    if fortfile.split('.')[-1]=='13' or fortfile.split('.')[0]=='f13':
        velplot.read_fort13(fortfile)
    if fortfile.split('.')[-1]=='26' or fortfile.split('.')[0]=='f26':
        velplot.read_fort26(fortfile)
    velplot.get_dv(dvplot)
    velplot.create_chunks(fortfile,pcvals,version)
    if show:
        fig = plt.figure(figsize=(9,2*len(velplot.table1)),frameon=False,dpi=300)
        for i in range(len(velplot.table1)):
            plt.subplots_adjust(left=0.05, right=0.95, bottom=0.06, top=0.96, wspace=0, hspace=0.05)
            ax = fig.add_subplot(len(velplot.table1),1,i+1,xlim=[-velplot.dv,velplot.dv],ylim=[-0.6,2.1])
            ax.yaxis.set_major_locator(plt.FixedLocator([0,1]))
            if velplot.extra!=None:
                for extrav in velplot.extra.split(':'):
                    ax.axvline(float(extrav),color='0.5',ls='dotted',lw=0.8)
            ax.text(-velplot.dv,1.6,r'$-1\sigma$  ',ha='right',va='center',size=8)
            ax.text(-velplot.dv,1.8,r'$+1\sigma$  ',ha='right',va='center',size=8)
            if i==0: plt.title(os.path.abspath(fortfile),fontsize=7)
            if i+1<len(velplot.table1): plt.setp(ax.get_xticklabels(), visible=False)
            else: ax.set_xlabel('Velocity relative to $z_{abs}=%.6f$ (km/s)'%velplot.zmid,fontsize=10)
            print velplot.header[i,0],velplot.header[i,1],velplot.table1[i][0],'chunks/vpfit_chunk'+'%03d'%(i+1)
            velplot.check_shift(i)
            velplot.plot_fit(i,daoaun,nores,unscale,getwave,details)
        plt.show()
        plt.close()
    else:
        pdf_pages = PdfPages(velplot.filename+'.pdf')
        i=0
        while (i<len(velplot.table1)):
            f   = 1             
            ref = i + 6          # position in table1 to define where to create new plotting page
            fig = plt.figure(figsize=(8.27, 11.69))
            plt.axis('off')
            plt.subplots_adjust(left=0.1, right=0.9, bottom=0.06, top=0.96, wspace=0, hspace=0)
            while i<len(velplot.table1) and i<ref:
                ax = fig.add_subplot(6,1,f,xlim=[-velplot.dv,velplot.dv],ylim=[-0.6,2.1])
                ax.yaxis.set_major_locator(plt.FixedLocator([0,1]))
                if velplot.extra!=None:
                    for extrav in velplot.extra.split(':'):
                        ax.axvline(float(extrav),color='0.5',ls='dotted',lw=0.8)
                ax.text(-velplot.dv,1.6,r'$-1\sigma$ ',ha='right',va='center',size=8)
                ax.text(-velplot.dv,1.8,r'$+1\sigma$ ',ha='right',va='center',size=8)
                if f==1: plt.title(os.path.abspath(fortfile),fontsize=7)
                if i+1!=ref and i+1!=len(velplot.table1): plt.setp(ax.get_xticklabels(), visible=False)
                else: ax.set_xlabel('Velocity relative to $z_{abs}=%.6f$ (km/s)'%velplot.zmid,fontsize=10)
                print velplot.header[i,0],velplot.header[i,1],velplot.table1[i][0],'chunks/vpfit_chunk'+'%03d'%(i+1)
                velplot.check_shift(i)
                velplot.plot_fit(i,daoaun,nores,unscale,getwave,details)
                i = i + 1
                f = f + 1
            pdf_pages.savefig(fig)
        pdf_pages.close()

if __name__ == "__main__":

    if '-h' in sys.argv or '--help' in sys.argv:
        velplot.show_help()
    else:
        make_figure()
