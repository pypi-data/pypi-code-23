import velplot,os,numpy
import astropy.io.fits as fits

def read_spec(i):
    '''
    Read spectrum and extract wavelength and flux dataset.
    '''
    specfile = velplot.table1[i][0]
    datatype = specfile.split('.')[-1]
    wavefile = specfile.replace('.fits','.wav.fits')
    if datatype=='fits' and os.path.exists(wavefile)==True:
        fh = fits.open(wavefile)
        hd = fh[0].header
        velplot.specwa = fh[0].data
        fh = fits.open(specfile)
        hd = fh[0].header
        velplot.specfl = fh[0].data        
    elif datatype=='fits':
        fh = fits.open(specfile)
        hd = fh[0].header
        d  = fh[0].data
        if ('CTYPE1' in hd and hd['CTYPE1'] in ['LAMBDA','LINEAR']) or ('DC-FLAG' in hd and hd['DC-FLAG']=='0'):
            velplot.specwa = hd['CRVAL1'] + (hd['CRPIX1'] - 1 + numpy.arange(hd['NAXIS1']))*hd['CDELT1']
        else:
            velplot.specwa = 10**(hd['CRVAL1'] + (hd['CRPIX1'] - 1 + numpy.arange(hd['NAXIS1']))*hd['CDELT1'])
        if len(d.shape)==1:
            velplot.specfl = d[:]
        else:
            velplot.specfl = d[0,:]
    else:
        d = numpy.loadtxt(specfile,comments='!')
        velplot.specwa = d[:,0]
        velplot.specfl = d[:,1]
