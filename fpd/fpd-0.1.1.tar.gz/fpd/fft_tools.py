from __future__ import print_function
import matplotlib.pylab as plt
import numpy as np

from numpy.fft import fft2, ifft2, fftshift, ifftshift, fftfreq
from scipy.ndimage import gaussian_filter
from matplotlib.widgets import Slider
from matplotlib.widgets import RadioButtons


plt.ion()



# TODO could specify s for faster fft in fft2 etc



def fft2rdf(rrf, im_fft):
    '''
    Calculate radial distribution of fft image.
    
    Parameters
    ----------
    im_fft : ndarray
        2-D array of absolute FFT value.
    rrf : ndarray
        2-D array of FFT frequency magnitudes.
    
    Returns
    -------
    r : 1-D array
        Frequency array.
    radial_mean : 1-D array
        Average radial distribution.
    
    '''
    
    r_scale = 1.0/rrf.max() * np.sqrt(2)*im_fft.shape[0]
    rrf = rrf * r_scale 
    rrf_int = rrf.astype(int)

    tbin = np.bincount(rrf_int.ravel(), im_fft.ravel())
    nr = np.bincount(rrf_int.ravel())
    with np.errstate(invalid='ignore', divide='ignore'):
        radial_mean = tbin / nr
    r = np.arange(radial_mean.shape[0]) / r_scale
    
    return r, radial_mean


def _gen_mask(rrf, fminmax, gy, mode='circ'):
    modes = ['circ', 'horiz', 'vert']
    if mode.lower() not in modes:
        raise NotImplementedError
    rrf = rrf.copy()
    imr, imc = rrf.shape
    fmin, fmax = fminmax
    gx = gy*float(imc)/imr
    g = (gy, gx)
    if mode == modes[0]:
        pass
    elif mode == modes[1]:
        xfreq = rrf[int(rrf.shape[0]/2), :]
        rrf = rrf*0 + xfreq[None, :]
    elif mode == modes[2]:
        yfreq = rrf[:, int(rrf.shape[1]/2)]
        rrf = rrf*0 + yfreq[:, None]
    mask = np.logical_and(rrf>=fmin, rrf<=fmax)
    mask = gaussian_filter(mask*1.0, g)
    return mask


def _gen_im_pass(imf, mask):
    ''' mask non-quad swapped FFT imf with mask and return real ifft'''
    im_pass = ifft2(imf * ifftshift(mask)).real
    return im_pass 


def bandpass(im, fminmax, gy, mask=None, full_out=False, mode='circ'):
    '''
    Basic bandpass filter, accepting multiple images at once.
    
    Parameters
    ----------
    im : ndarray
        Array of images to be filtered, with images in last 2 dimensions.
        The images need not be square.
    fminmax : length 2 iterable
        Minimum and maximum frequencies of band in 1/pixels.
    gy : scalar
        Gaussian sigma for edge smoothing in (fft) pixels.
        The x-axis value is calculated to match.
    mask : 2-D array or None
        If None, `fminmax` is used to generate mask.
        Else, the passed array with values 0-1 is used directly.  
    full_out : bool
        If True, additional outputs are returned.
    mode : str
        Type of bandpass in ['circ', 'horiz', 'vert']
        
    Returns
    -------
    Tuple of (im_pass, (im_fft, mask, extent)
    
    im_pass : ndarray
        Filtered images.
    im_fft : ndarray
        Absolute value of FFT.
    mask : ndarray
        Float mask image.
    extent : tuple
        FFT and mask image extent (left, right, top, bottom).
    
    If `full_out`, also returned are a tuple of (rrf, yf, xf, imf):
    
    rrf : ndarray
        2-D array of FFT frequency magnitudes.
    yf : ndarray
        1-D array of FFT y-axis frequencies.
    xf : ndarray
        1-D array of FFT x-axis frequencies.
    imf : ndarray
        Unswapped 2-D array of complex FFT.
        
    Examples
    --------
    Filter random noise image:
    
    >>> import numpy as np
    >>> from fpd.fft_tools import bandpass
    
    >>> im = np.random.rand(*(256,)*2)-0.5
    >>> im_pass, (im_fft, mask, extent) = bandpass(im, (1.0/12, 1.0/5), gy=2)
    
    >>> _ = plt.matshow(im)
    >>> _ = plt.matshow(im - 0.5*im_pass)
    >>> _ = plt.matshow(im - im_pass)   
    >>> _ = plt.matshow(im_fft, extent=extent)
    >>> _ = plt.matshow(mask, extent=extent)

    '''

    modes = ['circ', 'horiz', 'vert']
    if mode.lower() not in modes:
        raise NotImplementedError
    
    fmin, fmax = fminmax
    im_shape = im.shape
    imr, imc = im_shape[-2:]

    yf, xf = [fftshift(fftfreq(t)) for t in (imr, imc)]
    extent = (xf.min(), xf.max(), yf.max(), yf.min())

    xyf = np.meshgrid(xf, yf, indexing='xy')
    #xxf, yyf = xyf
    rrf = np.linalg.norm(xyf, ord=None, axis=0)
    
    imf = fft2(im, s=None, axes=(-2, -1), norm=None)
    im_fft = np.abs(fftshift(imf, axes=(-2, -1)))
    
    if mask is None:
        mask = _gen_mask(rrf, fminmax, gy, mode)
    else:
        mask = mask
    im_pass = _gen_im_pass(imf, mask)   
    
    out = (im_pass, (im_fft, mask, extent))
    if full_out:
        out += ((rrf, yf, xf, imf),)
    return out


class BandpassPlotter:
    def __init__(self, im, fminmax=(0, 0.5), gy=2, fact=0.75, cmap='gray', blit=True, mode='circ'):
        '''
        Interactive plotting of bandpass filter.
        See `bandpass` for documentation.
        
        Parameters
        ----------
        fact : scalar [0: 1]
            Factor of passed data subtracted from data (middle plot).
        cmap : matplotlib cmap
            Colourmap used for image plotting.
        blit : bool
            Controls blitting of plot updates.
        
        Examples
        --------
        >>> import matplotlib.pylab as plt
        >>> import numpy as np
        >>> import fpd
        >>> plt.ion()
        
        >>> py, px = 32.0, 16.0
        >>> y, x = np.indices((256,)*2)
        >>> im = np.sin(y/py*2*np.pi) + np.sin(x/px*2*np.pi)
        
        >>> b = fpd.fft_tools.BandpassPlotter(im, fminmax=(0.045, 0.08), gy=1, fact=1)
        
        '''     
        
        self.im = im
        self.fmin, self.fmax = fminmax
        self.gy = gy
        self.cmap = cmap
        self.blit = blit
        self.fact = fact
        self.mode = mode
        self.calc_data(first=True)
        self.init_fig()
        self.init_plots()
    
    
    def calc_data(self, first=False, level=0):
        out = bandpass(self.im, (self.fmin, self.fmax), gy=self.gy, full_out=first, mode=self.mode)
        if first:
            im_pass, (im_fft, mask, extent), (rrf, yf, xf, imf) = out
            self.extent = extent
            self.yf = yf
            self.xf = xf
            self.rrf = rrf
            self.imf = imf
            
            self.im_pass = im_pass
            self.im_fft = im_fft
            self.mask = mask
            
            # rdf
            self.r, self.radial_mean = fft2rdf(self.rrf, im_fft)   
        else:
            # update
            if level <= 1:
                self.mask = _gen_mask(self.rrf, (self.fmin, self.fmax), self.gy, self.mode)
            if level <= 2:
                self.im_pass = _gen_im_pass(self.imf, self.mask)        
        if level <= 3:
            self.im_dif = self.im - self.fact*self.im_pass   


    
    def init_fig(self):
        nr, nc = self.im_pass.shape
        woh = float(nc)/nr
        
        self.fig = plt.figure(figsize=(9.25, 7.5))
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        plt.set_cmap(self.cmap)
        
        # axes
        gs = plt.mpl.gridspec.GridSpec(2, 3, 
                                       left=None, bottom=0.25, right=None, top=None,
                                       wspace=None, hspace=None, 
                                       width_ratios=None, height_ratios=None)
        self.ax_im = plt.subplot(gs[0, 0])
        self.ax_im_dif = plt.subplot(gs[0, 1], sharey=self.ax_im, sharex=self.ax_im)
        self.ax_im_dif.set_xlabel('pix')
        self.ax_im_pass = plt.subplot(gs[0, 2], sharey=self.ax_im, sharex=self.ax_im)
        
        self.ax_mask = plt.subplot(gs[1, 0])
        self.ax_fft = plt.subplot(gs[1, 1], sharey=self.ax_mask, sharex=self.ax_mask)
        self.ax_fft.set_xlabel('1/pix')
        self.ax_rdf = plt.subplot(gs[1, 2])
        
        
        self.ax_mask.minorticks_on()
        self.ax_fft.minorticks_on()
        
        
        # sliders
        axcolor = 'lightgoldenrodyellow'
        
        if int(plt.matplotlib.__version__.split('.') [0]) >= 2:
            d = {'facecolor': axcolor}
        else:
            d = {'axisbg': axcolor}
        
        axfmin = plt.axes([0.25, 0.02, 0.65, 0.025], **d)
        axfmax = plt.axes([0.25, 0.06, 0.65, 0.025], **d)
        axsig = plt.axes([0.25, 0.10, 0.65, 0.025], **d)
        axfact = plt.axes([0.25, 0.14, 0.65, 0.025], **d)
        
        v = '%1.3f'
        self.sfmin = Slider(axfmin, 'Fmin', 0.0, np.sqrt(2)*0.5,
                            valinit=self.fmin, valfmt=v)
        self.sfmax = Slider(axfmax, 'Fmax', 0.0, np.sqrt(2)*0.5,
                            valinit=self.fmax, valfmt=v)
        self.ssig = Slider(axsig, 'Sigma', 0.0, 10.0,
                           valinit=self.gy, valfmt=v)
        self.sfact = Slider(axfact, 'Factor', 0.0, 1.0,
                            valinit=self.fact, valfmt=v)
        
        self.sfmin.on_changed(self.update_mask)
        self.sfmax.on_changed(self.update_mask)
        self.ssig.on_changed(self.update_mask)
        self.sfact.on_changed(self.update_fact)
        
        # buttons
        norm_ax = plt.axes([0.02, 0.02, 0.07, 0.07], **d)
        self.rnorm = RadioButtons(norm_ax, ('Lin', 'Log'))
        self.rnorm.on_clicked(self.update_norm)
        
        mode_ax = plt.axes([0.02, 0.10, 0.07, 0.10], **d)
        labels = ['circ', 'horiz', 'vert']
        mode_ind = labels.index(self.mode)
        self.rmode = RadioButtons(mode_ax, labels)
        self.rmode.on_clicked(self.update_mode)
        self.rmode.eventson = False
        self.rmode.set_active(mode_ind)
        self.rmode.eventson = True
        
    def update_mode(self, label):
        self.mode = label
        # TODO: change overlays between lines / circles 
        self.update_mask(None)
        plt.draw()
    
    def update_norm(self, label):
        norm_dict = {'Lin': plt.mpl.colors.NoNorm, 'Log': plt.mpl.colors.LogNorm}
        norm = norm_dict[label]
        self.ax_fft.images[0].set_norm(norm())
        plt.draw()
    
    def on_scroll(self, event):
        ss = [self.sfmin, self.sfmax, self.ssig, self.sfact]
        axs = [s.ax for s in ss]
        try:
            ind = axs.index(event.inaxes)
        except ValueError:
            # not in any axis we want
            return
        # we are in an axis
        s = ss[ind]
        v = s.val
        vmin, vmax = s.valmin, s.valmax
        step = (vmax-vmin)/100.0

        if event.button == 'down':
            nv = v - step
        elif event.button == 'up':
            nv = v + step
        if nv < vmin:
            nv = vmin
        if nv > vmax:
            nv = vmax
        s.set_val(nv)
        
        if ind == 3:
            self.update_fact(None)
        else:
            self.update_mask(None)
        
    
    def init_plots(self):
        self.ax_im.imshow(self.im, interpolation='nearest')
        self.ax_im.set_title('Image')
        
        self.ax_fft.imshow(self.im_fft, extent=self.extent,
                           interpolation='nearest')
        self.fmin_circle = plt.Circle((0, 0), self.fmin, edgecolor='r',
                                      facecolor='none', lw=0.5)
        self.fmax_circle = plt.Circle((0, 0), self.fmax, edgecolor='r',
                                      facecolor='none', lw=0.5)
        self.ax_fft.add_artist(self.fmin_circle)
        self.ax_fft.add_artist(self.fmax_circle)
        
        numrows, numcols = self.im_fft.shape
        def format_coord(x, y):
            col = int(x + 0.5)
            row = int(y + 0.5)
            if col>=0 and col<numcols and row>=0 and row<numrows:
                z = self.im_fft[row,col]
                r = (x**2+y**2)**0.5
                return 'x=%0.4f, y=%0.4f, r=%0.4f'%(x, y, r)
            else:
                return 'x=%1.4f, y=%1.4f' %(x, y)
        self.ax_fft.format_coord = format_coord

        
        self.ax_im_dif_im = self.ax_im_dif.imshow(self.im_dif, interpolation='nearest')
        self.ax_im_dif.set_title('Im - f*Pass')
        self.ax_im_pass_im = self.ax_im_pass.imshow(self.im_pass, interpolation='nearest')
        self.ax_im_pass.set_title('Pass')
        self.ax_mask_im = self.ax_mask.imshow(self.mask, extent=self.extent, 
                                              interpolation='nearest', 
                                              vmin=0, vmax=1)
        self.ax_mask.set_title('Mask')
        
        self.ax_rdf_line, = self.ax_rdf.semilogy(self.r, self.radial_mean, '-k')
        self.fmin_l = self.ax_rdf.axvline(self.fmin, color='r', lw=0.5)
        self.fmax_l = self.ax_rdf.axvline(self.fmax, color='r', lw=0.5)
        
        self.fig.canvas.draw_idle()
    
    
    def update_plots(self):
        if self.blit:
            # blitting
            axs = self.fig.axes[1:6]
            backgrounds = [self.fig.canvas.copy_from_bbox(ax.bbox) for ax in axs]
            
            for i, (ax, bk) in enumerate(zip(axs, backgrounds)):
                if i != 3:
                    # skip fft
                    self.fig.canvas.restore_region(bk)
        
        # set data
        self.ax_im_dif_im.set_data(self.im_dif)
        self.ax_im_dif_im.set_clim(self.im_dif.min(), self.im_dif.max())
        
        self.fmin_circle.set_radius(self.fmin)
        self.fmax_circle.set_radius(self.fmax)
        
        self.ax_im_pass_im.set_data(self.im_pass)
        self.ax_im_pass_im.set_clim(self.im_pass.min(), self.im_pass.max())
        
        self.ax_mask_im.set_data(self.mask)
        
        self.fmin_l.set_xdata([self.fmin,]*2)
        self.fmax_l.set_xdata([self.fmax,]*2)
        
        if not self.blit:
            self.fig.canvas.draw_idle()
        else:
            # blitting
            artists = [self.ax_im_dif_im, self.ax_im_pass_im, 
                    self.ax_mask_im, [self.fmin_circle, self.fmax_circle],
                    [self.fmin_l, self.fmax_l]]
            for ax, a in zip(axs, artists):
                if isinstance(a, list):
                    [ax.draw_artist(ai) for ai in a]
                else:
                    ax.draw_artist(a)
                self.fig.canvas.blit(ax.bbox)
            
    
    def update_mask(self, val):
        self.fmin = self.sfmin.val
        self.fmax = self.sfmax.val
        self.gy = self.ssig.val
        self.calc_data(0)
        self.update_plots()
        
        
    def update_fact(self, val):
        self.fact = self.sfact.val
        self.calc_data(3)
        self.update_plots()

