def python_model():
    
    id=458
    
    from astropy.modeling import models, fitting
    import astropy.io.fits as pyfits
    import numpy as np
    from stsci.convolve import correlate2d
    
    from research.grizli import galfit
    reload(galfit)
    
    s0 = galfit.GalfitSersic(pos=[64.689, 65.17], mag=19.17, n=3.82, q=0.77, pa=-57.9, R_e=9.7789)
    sers = models.Sersic2D(amplitude=1, r_eff=s0['R_e'], n=s0['n'], x_0=s0['pos'][0], y_0=s0['pos'][1], ellip=1-s0['q'], theta=s0['pa']/180*np.pi+np.pi/2)

    psf = pyfits.open('/tmp/gf_psf.fits')[0].data
    mask = pyfits.open('/tmp/gf_mask.fits')[0].data == 0
    rms = pyfits.open('/tmp/gf_rms.fits')[0].data
    sci = pyfits.open('/tmp/gf_sci.fits')[0].data
    
    sh = sci.shape
    #rms = np.ones(sh)*np.median(rms)
    
    ZP = 26.563
    sers = models.Sersic2D(amplitude=0.2, r_eff=5., n=4., x_0=sh[1]/2., y_0=sh[0]/2., ellip=0.05, theta=0)
    
    fit, q, theta = galfit.fit_gauss(sci)
    #theta += np.pi/2
    theta = np.pi
    sers = models.Sersic2D(amplitude=0.2, r_eff=5., n=4., x_0=sh[1]/2., y_0=sh[0]/2., ellip=1-q, theta=theta)#, fixed={'theta':True})
    sers1 = models.Sersic2D(amplitude=0.2, r_eff=5., n=4., x_0=sh[1]/2., y_0=sh[0]/2., ellip=1-q, theta=theta, fixed={'x_0':True, 'y_0':True})#, fixed={'theta':True})

    s1 = models.Sersic2D(amplitude=0.2, r_eff=5., n=1., x_0=sh[1]/2., y_0=sh[0]/2., ellip=1-q, theta=theta, fixed={'n':True, 'x_0':True, 'y_0':True})
    s4 = models.Sersic2D(amplitude=0.2, r_eff=5., n=4., x_0=sh[1]/2., y_0=sh[0]/2., ellip=1-q, theta=theta, fixed={'n':True, 'x_0':True, 'y_0':True})
    
    poly = models.Polynomial2D(degree=1, c0_0=0, fixed={'c0_0':True})
    
    components = [s1, s4]
    
    #components = [sers]#, s1]
    components = [sers]#, s1, poly] #s4, s1]
    components = [sers, s1, s4, poly] #s4, s1]
    
    x0 = []
    param_names = []
    for ic, comp in enumerate(components):
        for i, p in enumerate(comp.param_names):
            if not comp.fixed[p]:
                x0.append(comp.parameters[i])
                param_names.append('{0}_{1}'.format(p, ic))
                
    data = [xp, yp, sci, rms, mask, psf]
    
    from scipy.optimize import least_squares
    reload(galfit)
    
    lm_args = (components, data, 'lm')
    model_args = (components, data, 'model')

    #step = np.array([0.1, 0.5, 0.1, 0.1, 0.1, 0.1, 1])
    step = None
    
    limits = {'amplitude':[0,5], 'r_eff':[0.1, 50], 'n':[0.1, 20], 'x_0':[sh[1]/2-3, sh[1]/2+3], 'y_0':[sh[0]/2.-3, sh[0]/2.+3], 'ellip':[0.05,1], 'theta':[-2*np.pi, 2*np.pi]}
    pstep = {'amplitude':0.05, 'r_eff':0.2, 'n':0.1, 'x_0':0.1, 'y_0':0.1, 'ellip':0.05, 'theta':0.1}

    bounds = []
    step = []
    for p in param_names:
        if p[:-2] in limits:
            bounds.append(limits[p[:-2]])
            step.append(pstep[p[:-2]])
        else:
            bounds.append([-np.inf, np.inf])
            step.append(1.e-5)
            
    bounds = np.array(bounds).T
    #bounds = (-np.inf, np.inf)
    
    for iter in range(5):
        fit = least_squares(galfit._objfun, x0, jac='2-point', bounds=bounds, method='trf', ftol=1e-08, xtol=1e-08, gtol=1e-08, x_scale=1., loss='huber', f_scale=1.0, diff_step=step, tr_solver=None, tr_options={}, jac_sparsity=None, max_nfev=1000, verbose=1, args=lm_args)
        
        x0 = fit.x
        
    fit.pdict = OrderedDict()
    for i in range(len(fit.x)):
        fit.pdict[param_names[i]] = fit.x[i]
        
    sers_model = galfit._objfun(fit.x, *model_args)
    
    resid = galfit._objfun(fit.x, *lm_args)
    
def _objfun(params, components, data, ret):
    from stsci.convolve import correlate2d
    
    xp, yp, sci, rms, mask, psf = data

    smodel = sci*0
    ix = 0
    for ic, comp in enumerate(components):
        for i, p in enumerate(comp.param_names):
            if not comp.fixed[p]:
                comp.parameters[i] = params[ix]
                ix += 1
        
        if ic > 0:
            for p in ['x_0' ,'y_0', 'ellip', 'theta']:
                if p in comp.fixed:
                    if comp.fixed[p]:
                        pi = comp.param_names.index(p)
                        c0 = components[0].param_names.index(p)
                        comp.parameters[pi] = components[0].parameters[c0]
            
        smodel += comp(xp, yp)
                
    # for i, p in enumerate(param_names):
    #     sers.parameters[sers.param_names.index(p)] = params[i]
    
    smodel_psf = correlate2d(smodel, psf, fft=1)
    
    if ret == 'model':
        return smodel_psf
    
    if ret == 'lm':
        #print(sers.__repr__())
        return (sci-smodel_psf)[mask]/rms[mask]
        
def fit_ID_list(root='sdssj1723+3411', ids=[449, 371, 286, 679, 393, 576, 225], filter='f140w', ds9=None, ds9_frame=None):
    """
    """
    import astropy.io.fits as pyfits
    from grizli.galfit import galfit
    from grizli.galfit.galfit import GalfitSersic, GalfitExpdisk
    
    if False:
        #### Testing
        reload(galfit)
        filter = 'f140w'
    
        root = 'sdssj1723+3411'
        ids = [449, 371, 286, 679, 393, 576, 225]

        root = 'sdssj2340+2947'
        ids = [486, 463]#, 439]

    self = galfit.Galfitter(root=root, filter=filter, galfit_exec='../Galfit/galfit')
        
    #comps = [GalfitSersic(n=4)]
    comps = [GalfitSersic(n=4), galfit.GalfitExpdisk()]
    comps = [GalfitSersic(n=4, dev=True), galfit.GalfitExpdisk()]
    comps = [GalfitSersic(n=4, dev=True), GalfitSersic(n=4)]
    
    # Fit galfit components
    for id in ids:
        res = self.fit_object(id=id, radec=(None, None), size=30, get_mosaic=True, components=comps, recenter=True, gaussian_guess=False)
        
        if ds9:
            im = pyfits.open('{0}-{1}_galfit_{2:05d}.fits'.format(root, filter, id))
            if ds9_frame is not None:
                ds9.frame(ds9_frame)
            
            ds9.view(self.sci[0].data - im[0].data/self.sci[0].header['EXPTIME'], header=self.sci[0].header)
    
    ###############
    # Combine components into a single image and make new segmentation images
    full_model = self.sci[0].data*0
    full_seg = self.seg[0].data*0
    orig_seg = self.seg[0].data*1
    
    seg_threshold = 0.001
    
    for id in ids:
        im = pyfits.open('{0}-{1}_galfit_{2:05d}.fits'.format(root, filter, id))
        full_model += im[0].data/self.sci[0].header['EXPTIME']
        full_seg[(im[0].data > seg_threshold) & (full_seg == 0)] = id
        orig_seg[(orig_seg == id)] = 0
        
        if ds9:
            if ds9_frame is not None:
                ds9.frame(ds9_frame)
            
            ds9.view(self.sci[0].data - full_model)
    
    # Model-subtracted image
    pyfits.writeto('{0}-{1}_galfit_clean.fits'.format(root, filter), data=self.sci[0].data-full_model, header=self.sci[0].header, clobber=True)
    
    # Model image
    pyfits.writeto('{0}-{1}_galfit.fits'.format(root, filter), data=full_model, header=self.sci[0].header, clobber=True)
    
    # Segmentation image where galfit models > `seg_threshold`
    pyfits.writeto('{0}-{1}_galfit_seg.fits'.format(root, filter), data=full_seg, header=self.seg[0].header, clobber=True)
    
    # Segmentation image with the fitted object IDs removed
    pyfits.writeto('{0}-{1}_galfit_orig_seg.fits'.format(root, filter), data=orig_seg, header=self.seg[0].header, clobber=True)
    