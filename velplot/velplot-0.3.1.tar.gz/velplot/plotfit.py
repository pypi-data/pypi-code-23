import velplot,numpy,sys
import matplotlib.pyplot as plt
from matplotlib import re
from scipy.ndimage import gaussian_filter1d

def plot_fit(i,daoaun,nores,unscale,getwave,details):
    '''
    Plot system and model.
    
    Parameters
    ----------
    i : int
      Index of the fitting region.
    daoaun : float
      Unit of da/a value in VPFIT.
    nores : bool
      Flag to not plot residuals
    unscale : bool
      Flag to not correct the data and distort the models
    getwave : bool
      Flag to get wavelength array from the spectrum
    details : bool
      Flag to plot individual Voigt profiles
    '''
    # Load data and model
    chunk = numpy.loadtxt('chunks/vpfit_chunk'+'%03d'%(i+1)+'.txt',comments='!')
    ibeg    = abs(chunk[:,0]-velplot.table1[i][2]).argmin()+1 if velplot.table1[i][2]!=velplot.table1[i][3] else 0
    iend    = abs(chunk[:,0]-velplot.table1[i][3]).argmin()-1 if velplot.table1[i][2]!=velplot.table1[i][3] else -1
    velplot.wa = chunk[ibeg:iend,0]
    velplot.fl = chunk[ibeg:iend,1]
    velplot.er = chunk[ibeg:iend,2]
    velplot.mo = chunk[ibeg:iend,3]
    wamid   = float(velplot.comment[i,2])
    pos     = abs(velplot.wa-wamid).argmin()
    vel     = 2*(velplot.wa-wamid)/(velplot.wa+wamid)*velplot.c
    # Estimate the half-pixel size to shift the steps of the flux array when plotting
    pos    = abs(velplot.wa-(velplot.table1[i][2]+velplot.table1[i][3])/2).argmin()
    pix1   = velplot.wa[pos]
    pix2   = (velplot.wa[pos]+velplot.wa[pos-1])/2
    dempix = 2*(pix1-pix2)/(pix1+pix2)*velplot.c
    # Plot residuals based on the flux, error, and model from the chunks
    plt.axhline(y=1.6,color='magenta',zorder=2,lw=0.3)
    plt.axhline(y=1.7,color='magenta',ls='dotted',zorder=2,lw=0.3)
    plt.axhline(y=1.8,color='magenta',zorder=2,lw=0.3)
    if nores==False and velplot.table1[i][2]!=velplot.table1[i][3]:
        velo = vel if unscale else vel+velplot.shift
        res  = (velplot.fl-velplot.mo)/velplot.er/10+1.7
        plt.plot(velo+dempix,res,lw=0.5,drawstyle='steps',color='magenta',zorder=3)
    # Plot model corrected for floating zero and continuum and velocity shift
    if velplot.table1[i][2]!=velplot.table1[i][3]:
        corr   = velplot.cont+velplot.slope*(velplot.wa/((1+velplot.z)*1215.6701)-1)
        model  = velplot.mo/corr+velplot.zero
        model  = model / (1+velplot.zero)
        model  = velplot.mo if unscale else model
        velo   = vel if unscale else vel+velplot.shift
        plt.plot(velo,model,lw=1.,color='lime',alpha=0.8,zorder=1)
        plt.plot(velo+dempix,velplot.er,lw=.1,drawstyle='steps',color='cyan')
    # Plot data
    if getwave:
        velplot.read_spec(i)
        wabeg   = wamid * (2*velplot.c-velplot.dv) / (2*velplot.c+velplot.dv)
        waend   = wamid * (2*velplot.c+velplot.dv) / (2*velplot.c-velplot.dv)
        ibeg    = abs(velplot.specwa-wabeg).argmin()
        iend    = abs(velplot.specwa-waend).argmin()
        ibeg    = ibeg-1 if ibeg>0 else ibeg
        iend    = iend+1 if iend<len(velplot.specwa)-1 else iend
        velplot.wa = velplot.specwa[ibeg:iend]
        velplot.fl = velplot.specfl[ibeg:iend]
        pos     = abs(velplot.wa-wamid).argmin()
        vel     = 2*(velplot.wa-wamid)/(velplot.wa+wamid)*velplot.c
    corr   = velplot.cont+velplot.slope*(velplot.wa/((1+velplot.z)*1215.6701)-1)
    flux   = velplot.fl/corr + velplot.zero
    flux   = flux / (1+velplot.zero)
    flux   = velplot.fl if unscale else flux
    velo   = vel if unscale else vel+velplot.shift
    plt.plot(velo+dempix,flux,drawstyle='steps',lw=0.3,color='black',zorder=2)
    # Prepare high dispersion wavelength array
    start  = wamid * (2*velplot.c-velplot.dv) / (2*velplot.c+velplot.dv)
    end    = wamid * (2*velplot.c+velplot.dv) / (2*velplot.c-velplot.dv)
    val    = 1
    wave   = [start-2]
    dv     = velplot.dispersion
    while wave[-1]<end+2:
        wave.append(wave[-1]*(2*velplot.c+dv)/(2*velplot.c-dv))
    wave   = numpy.array(wave)
    vel    = 2*(wave-wamid)/(wave+wamid)*velplot.c
    vel    = vel-velplot.shift if unscale else vel
    model  = [1]*len(vel)
    show   = []
    for k in range(len(velplot.table2)):
        complist = numpy.empty((0,2))
        z = float(re.compile(r'[^\d.-]+').sub('',velplot.table2[k][2]))
        N = float(re.compile(r'[^\d.-]+').sub('',velplot.table2[k][1]))
        b = float(re.compile(r'[^\d.-]+').sub('',velplot.table2[k][3]))
        
        ''' Plot high dispersion Voigt profiles, lines, and labels for each component '''
                
        for p in range(len(velplot.atom)):
            
            alpha = velplot.table2[k][-2]*daoaun
            cond1 = velplot.table2[k][0]==velplot.atom[p,0]
            cond2 = velplot.table2[k][0] not in ['<>','>>','__','<<']
            cond3 = velplot.wa[0] < (1+z)*float(velplot.atom[p,1]) < velplot.wa[-1]

            if cond1 and cond2 and cond3:

                lambda0 = float(velplot.atom[p,1])

                if details:

                    q       = float(velplot.atom[p,5])
                    wavenum = 1./(lambda0*10**(-8))
                    wavenum = wavenum - q*(alpha**2-2*alpha)
                    lambda0 = 1/wavenum*10**(8)
                    f       = float(velplot.atom[p,2])
                    gamma   = float(velplot.atom[p,3])
                    profile = velplot.voigt_model(N,b,wave/(z+1),lambda0,gamma,f)
                    model   = model*profile
                    vsig    = velplot.table1[i][4]/dv
                    conv    = gaussian_filter1d(profile,vsig)
                    if unscale:
                        corr = velplot.cont+velplot.slope*(wave/((1+velplot.z)*1215.6701)-1)
                        conv = conv*corr-velplot.zero
                        conv = conv/(1-velplot.zero)
                    plt.plot(vel,conv,lw=0.2,color='orange')

                if velplot.atom[p,1]==velplot.header[i][1] or abs(float(velplot.atom[p,1])-float(velplot.header[i][1])) > 0.1:
                    
                    lobs  = lambda0*(z+1)
                    vobs  = 2*(lobs-wamid)/(lobs+wamid)*velplot.c
                    vobs  = vobs - velplot.shift if unscale else vobs
                    pos   = 1.08 if val%2==0 else 1.25
                    zdiff = abs(2*(z-velplot.zmid)/(z+velplot.zmid))
                    color = '#FF4D4D' if zdiff < 0.003 and velplot.atom[p,0]==velplot.header[i][0] and velplot.atom[p,1]==velplot.header[i][1] \
                            else '#9370db' if zdiff < 0.003\
                            else '#ba55d3' if zdiff > 0.003 and velplot.atom[p,0] in ['HI','??'] \
                            else 'darkorange'
    
                    plt.axvline(x=vobs,ls='dotted',color=color,lw=.5,zorder=1)
                    
                    lab1 = velplot.table2[k][-3]
                    lab2 = ''.join(re.findall('[a-zA-Z]+',velplot.table2[k][2][-2:]))
                    if velplot.table2[k][2][-1].isdigit()==True and str(lab1)+color not in show:
                        t = plt.text(vobs,pos,lab1,color=color,weight='bold',fontsize=7,horizontalalignment='center')
                        t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))
                        show.append(str(lab1)+color)
                        val = val + 1
                    elif velplot.table2[k][2][-1].isdigit()==False and lab2+color not in show:
                        t = plt.text(vobs,pos,lab2[-1],color=color,weight='bold',fontsize=7, horizontalalignment='center')
                        t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))
                        show.append(lab2+color)
                        val = val + 1                         
                    
    if details:

        vsig  = velplot.table1[i][4]/dv
        model = gaussian_filter1d(model,vsig)
        if unscale:
            corr  = velplot.cont+velplot.slope*(wave/((1+velplot.z)*1215.6701)-1)
            model = model*corr-velplot.zero
            model = model/(1-velplot.zero)
        plt.plot(vel,model,lw=1.,color='orange',alpha=.5,zorder=1)

    plt.axhline(y=1,color='black',ls='dotted',lw=0.3)
    plt.axhline(y=0,color='black',ls='dotted',lw=0.3)
    
