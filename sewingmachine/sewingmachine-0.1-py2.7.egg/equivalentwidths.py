import numpy as np
from scipy.interpolate import interp1d

def specewmeasure(spec, integration, windows,
                  sigmaclip=True,
                  sigma=2):
    spec_x = spec[:,0] #create arrays for spectra
    spec_y = spec[:,1]
    norm_pix = []
    norm_lambda = []
    windowmask = np.zeros(len(spec_x), dtype=bool)
    for i in windows:
        windowmask[(spec_x < i[1]) & (spec_x > i[0])] = 1
    cont_fit = np.polyfit(spec_x[windowmask],spec_y[windowmask], 1)
    cont_poly = np.poly1d(cont_fit)
    if sigmaclip == True:
        std = sigma*np.nanstd(spec_y[windowmask])
        residual = np.fabs(spec_y[windowmask] - cont_poly(spec_x[windowmask]))
        clip = residual < std
        windowmask[windowmask][clip] = 0
        cont_fit = np.polyfit(spec_x[windowmask],spec_y[windowmask], 1)
        cont_poly = np.poly1d(cont_fit)
    intmask = np.zeros(len(spec_x), dtype=bool)
    intmask[(spec_x <= integration[1]) & (spec_x >= integration[0])] = 1
    #linear interpolation of spectrum
    interpol = interp1d(spec_x, spec_y, kind='linear')
    line_x = np.zeros(len(spec_x[intmask])+2)
    line_y = np.zeros(len(spec_x[intmask])+2)
    line_x[1:-1] = spec_x[intmask]
    line_y[1:-1] = spec_y[intmask]
    #fractional pixels on blue and red side of line
    line_x[0] = integration[0]
    line_x[-1]= integration[1]
    line_y[0] = interpol(integration[0])
    line_y[-1] = interpol(integration[1])
    #continuum over the integration region
    cont_y = cont_poly(line_x)
    #normalise the flux over this range
    line_y = line_y/cont_y
    contarea = max(line_x)-min(line_x)
    linearea = np.trapz((1-line_y), x=line_x)
    return linearea
