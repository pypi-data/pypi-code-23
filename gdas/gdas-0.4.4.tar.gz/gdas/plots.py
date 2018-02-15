#!/usr/bin/env python
import matplotlib,numpy,math,mlpy
import matplotlib.pyplot as plt
from .retrieve            import time_convert
from astropy.units        import Quantity
from datetime             import datetime
from gwpy.table           import EventTable
from gwpy.plotter         import SegmentPlot,TimeSeriesPlot,FrequencySeriesPlot,SpectrogramPlot
from gwpy.segments        import SegmentList
from gwpy.frequencyseries import FrequencySeries
from gwpy.spectrogram     import Spectrogram
from gwpy.time            import from_gps
from gwpy.timeseries      import TimeSeries
from scipy                import signal

def plot_activity(full_seglist,t0=None,t1=None):
    """
    Plot full activity period for station.

    Parameters
    ----------
    full_seglist : dictionary
      Continuous list of available data in the selected time period
    """
    # Import gwpy tools
    plot = SegmentPlot()
    # Initialize plotting figure
    ax = plot.gca()
    # Plot all segment in figure
    ax.plot(full_seglist)
    if t0!=None and t1!=None:
        plot.axes[0].set_epoch(t0)
        ax.set_xlim(t0,t1)
    # Save figure
    plt.savefig("activity.png",dpi=300,transparent=True)

def plot_asd(station,data):
    """
    Plot Amplitude Spectral Density. AGG complexity starts to complain
    with large numbers of points. And we somehow invoke precision issues
    that need to be ameliorated.
    """
    if station!='fake':
        for d in data:
            d.x0 = Quantity(int(d.x0.value * 500), d.xunit)
            d.dx = Quantity(1, d.xunit)
        data.coalesce()
        for d in data:
            d.x0 = Quantity(d.x0.value / 500, d.xunit)
            d.dx = Quantity(0.002, d.xunit)
    # Initialize plotting functionality
    plot = FrequencySeriesPlot()
    # Loop over all the time series
    for d in data:
        # Generate 8 seconds per FFT with 4 second (50%) overlap
        spectrum = d.asd(8, 4)
        # Create plotting axis
        ax = plot.gca()
        # Plot square root of the spectrum
        ax.plot(numpy.sqrt(spectrum))
    # Set x axis to log scale
    ax.set_xscale('log')
    ax.set_xlabel('Frequency [Hz]')
    # Set y axis to log scale
    ax.set_yscale('log')
    ax.set_ylabel('Amplitude [pT]')
    # Set x axis limits
    ax.set_xlim(1e-1, 500)
    x = ax.get_xticklabels()
    def myticks(x,pos):
        if x == 0: return "$0$"
        exponent = int(numpy.log10(x))
        coeff = x/10**exponent
        if coeff==1:
            return r"$10^{{ {:2d} }}$".format(exponent)
        else:
            return r"${:2.0f} \times 10^{{ {:2d} }}$".format(coeff,exponent)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(myticks))
    plt.tight_layout()
    # Save figure
    plot.savefig("asd.png",dpi=300,transparent=True)
    
def plot_time_series(data,station='station-name',t0=None,t1=None,seglist=None,burst=None,fname='time_series'):
    """
    Generate a plot of the whole data time series
    """
    if type(data[0])==numpy.float64:
        data = [TimeSeries(data,sample_rate=data.sample_rate,epoch=data.start_time)]
    plot = TimeSeriesPlot(frameon=False)
    ax = plot.gca()
    # Loop over all the time series
    for ts in data:
        # Plot time series for each segment
        ax.plot(ts)
    # Display title
    ax.set_title('$\mathrm{'+station+'}$')
    ax.set_ylabel('Magnetic Field')
    # Plot fake signal
    if burst is not None:
        ax.plot(burst, color='red')
    # Plot activity segments
    if seglist!=None:
        activity = SegmentList(seglist[station].active)
        plotargs = {'label':'data present','facecolor':'g','edgecolor':'k'}
        plot.add_state_segments(activity,plotargs=plotargs)
    # Set limits
    if t0 is not None and t1 is not None:
        plot.axes[0].set_epoch(t0)
        plot.axes[1].set_epoch(t0)
        ax.set_xlim(t0,t1)
    # Fix exceeded cell block limit error
    plt.rcParams['agg.path.chunksize'] = 20000
    # Save figure
    plt.show() if fname==None else plot.savefig('%s.png'%fname)
    plt.close()
    
def plot_whitening(data,station='station-name',t0=None,t1=None,stride=20,fftlength=6,overlap=3,seglist=None,clog=False):
    """
    Generate a spectrogram plot and normalized spectrogram.
    norm: :math:`\sqrt{S(f,t)} / \sqrt{\overbar{S(f)}}`
    """
    if type(data[0])==float64:
        data = [TimeSeries(data,sample_rate=data.sample_rate,epoch=data.start_time)]
    # Setup plots
    plot = SpectrogramPlot()
    ax = plot.gca()
    white_plot = SpectrogramPlot()
    wax = white_plot.gca()
    # Loop through available time series
    for ts in data:
        #if (len(ts) * ts.dt).value < stride:
        #    continue
        spec = ts.spectrogram(stride,fftlength=fftlength,overlap=overlap)
        wspec = spec.ratio('median')
        if clog:
            ax.plot(spec,cmap='jet',norm=matplotlib.colors.LogNorm())
            wax.plot(wspec,vmin=0.1,vmax=100,cmap='jet',norm=matplotlib.colors.LogNorm())
        else:
            ax.plot(spec, cmap='jet')
            wax.plot(wspec,vmin=0.1,vmax=100,cmap='jet')
    # Define y axis and title
    ax.set_title('$\mathrm{'+station+'}$')
    ax.set_ylim(0.1, ts.sample_rate.value/2.)
    ax.set_yscale('log')
    wax.set_title('$\mathrm{'+station+'}$')
    wax.set_ylim(0.1, ts.sample_rate.value/2.)
    wax.set_yscale('log')
    plot.add_colorbar(label='Amplitude')
    white_plot.add_colorbar(label='Amplitude')
    # Plot activity panels for real data
    if seglist!=None:
        activity = SegmentList(seglist[station].active)
        plotargs = {'label':'data present','facecolor':'g','edgecolor':'k'}
        plot.add_state_segments(activity,plotargs=plotargs)
        white_plot.add_state_segments(activity,plotargs=plotargs)
    # Set plotting limits of x axis if edges defined
    if t0!=None and t1!=None:
        t0,t1 = time_convert(t0,t1)
        plot.axes[0].set_epoch(t0)
        plot.axes[2].set_epoch(t0)
        white_plot.axes[0].set_epoch(t0)
        white_plot.axes[2].set_epoch(t0)
        ax.set_xlim(t0,t1)
        wax.set_xlim(t0,t1)
    # Save figures
    plot.savefig("spectrogram.png",dpi=300,transparent=True)
    white_plot.savefig("whitened.png",dpi=300,transparent=True)
    plt.close()
    
def plot_triggers(filename='excesspower.xml.gz',fname='triggers.png'):
    """
    Plot excess power trigger results in a time-frequency frame.
    """
    events = EventTable.read(filename,format='ligolw.sngl_burst')
    #plot = events.plot('time','central_freq','duration','bandwidth',color='snr')
    time = events['peak_time'] + events['peak_time_ns'] * 1e-9
    events.add_column(events['peak_time'] + events['peak_time_ns'] * 1e-9, name='time')
    plot = events.plot('time','central_freq',color='snr',edgecolor='none')
    plot.axes[0].set_epoch(int(min(time)))
    plot.set_xlim((int(min(time)),round(max(time))))
    plot.set_ylabel('Frequency [Hz]')
    plot.set_yscale('log')
    #plot.set_title('GNOME '+station+' station event triggers')
    plot.add_colorbar(cmap='copper_r',label='Tile Energy')
    plt.savefig(fname,dpi=300,transparent=True)

def plot_bank(fdb):
    """
    Plot first filters from the filter bank in frequency domain.
    """
    plt.figure()
    for i, fdt in enumerate(fdb):
        if i==2:
            plt.plot(fdt.frequencies, fdt, 'k-')
            break
    plt.grid()
    #xmin = fdb[0].frequencies[0].value
    #xmax = fdb[-1].frequencies[-1].value
    #plt.xlim([xmin,xmax])
    plt.xlabel("frequency [Hz]")
    plt.savefig('bank.png',dpi=300,transparent=True)
    plt.close()

def plot_filters(tdb,fmin,band):
    """
    Plot first filters in time domain.
    """
    plt.figure()
    plt.subplots_adjust(left=0.2,right=0.95,bottom=0.15,top=0.95,hspace=0,wspace=1)
    for i, tdt in enumerate(tdb[:8:3]):
        ax = plt.subplot(3, 1, i+1)
        ax.plot(tdt.times.value - 2., numpy.real_if_close(tdt.value), 'k-')
        c_f = fmin + band/2 + 3 * (band*i) + 2.
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("%d Hz" % c_f)
        ax.set_xlim(25.0, 31.0)
        ax.set_ylim([-max(tdt.value), max(tdt.value)])
        #if i!=2: plt.setp(ax.get_xticklabels(), visible=False)
    plt.savefig('filters.png',dpi=300,transparent=True)
    plt.close()
    
def plot_ts(ts, fname="ts.png"):
    '''
    Plot time series data
    '''
    plot = TimeSeriesPlot()
    ax = plot.gca()
    ax.plot(TimeSeries(ts, sample_rate=1.0/ts.delta_t, epoch=ts.start_time))
    ax.set_xlim(ts.start_time,ts.end_time)
    plt.savefig(fname,transparent=True)
    plt.close()

def plot_spectrum(fd_psd):
    '''
    Plot power spectral density
    '''
    plot = FrequencySeriesPlot()
    ax = plot.gca()
    ax.plot(FrequencySeries(fd_psd, df=fd_psd.delta_f))
    #plt.ylim(1e-10, 1e-3)
    plt.xlim(0.1, 500)
    plt.loglog()
    plt.savefig("psd.png",dpi=300,transparent=True)
    plt.close()

def plot_spectrogram(spec,dt,df,ymax,t0,t1,fname="specgram.png"):
    '''
    Plot standard Fourier-based spectrogram
    '''
    plot = SpectrogramPlot()
    ax = plot.gca()
    ax.plot(Spectrogram(spec,dt=dt,df=df,epoch=float(t0)),cmap='viridis')
    plot.add_colorbar(label='Amplitude')
    plt.xlim(t0,t1)
    plt.ylim(0,ymax)
    plt.savefig(fname,transparent=True)#,dpi=300)
    plt.close()

def plot_tiles_ts(tdb,ndof,df,sample_rate,t0,t1,fname="tiles.png"):
    '''
    Plot time series for several channels
    '''
    fig = TimeSeriesPlot(figsize=(12,12))
    fig.suptitle('%i channels, %i Hz bandwidth, %i DOF'%(len(tdb),df,ndof))
    plt.subplots_adjust(left=0.03, right=0.97, bottom=0.07, top=0.95, hspace=0, wspace=0)
    for i, tdf in enumerate(tdb):
        ts_data = TimeSeries(tdf,epoch=float(t0),sample_rate=sample_rate)
        ax = fig.add_subplot(len(tdb),1,len(tdb)-i)
        ax.plot(ts_data)
        ax.set_xlim(t0,t1)
        if i>0:
            ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
    plt.savefig(fname,transparent=True)
    plt.close()

def plot_tiles_tf(tdb,ndof,df,ymax,sample_rate,t0,t1,fname="tiles.png"):
    '''
    Plot spectrogram for different tiles
    '''
    for i, tdf in enumerate(tdb):
        ts_data = TimeSeries(tdf,epoch=float(t0),sample_rate=sample_rate)
        f, t, Sxx = signal.spectrogram(tdf, sample_rate)
        plt.figure(figsize=(12,8))
        plt.subplots_adjust(left=0.1, right=0.97, bottom=0.07, top=0.95, hspace=0, wspace=0)
        plt.pcolormesh(t, f, Sxx)
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.ylim(0,ymax)
        plt.savefig(fname.replace('.png','_%03i.png'%i),transparent=True)
        plt.close()

def plot_spectrogram_from_ts(ts,fname='specgram.png'):
    '''
    Plot spectrogram
    '''
    plot = SpectrogramPlot()
    ax = plot.gca()
    ax.plot(Spectrogram(spec))
    #plt.ylim(1e-9, 1e-2)
    #plt.xlim(0.1, 500)
    #plt.loglog()
    plt.savefig(fname,transparent=True)
    plt.close()

def build_spec(data,tmin=None,tmax=None,fmin=None,fmax=None,vmin=None,vmax=None,
               mode='fourier',omega0=6,dt=1,dj=0.05,fct='morlet',
               stride=None,nfft=None,overlap=None,scale='log',station=None,
               dy=None,xmin=None,xmax=None,
               funit='Hz',tunit='secs',cmap='inferno',fname=None):
    """
    Plot multiplot figure with time series, PSD and spectrogram.

    Parameters
    ----------
    data : TimeSeries
      Magnetic field data
    tmin, tmax : datetime
      First and last timestamps
    fmin, fmax : float
      Minimum and maximum frequencies
    vmin, vmax : float
      Minimum and maximum color values
    mode : str
      Spectrogram mode, wavelet or Fourier. Default is Fourier
    omega0 : int
      Wavelet function parameter
    dt : float
      Time step
    dj : float
      Scale resolution (smaller values of dj give finer resolution)
    fct : str
      Wavelet function (morlet,paul,dog)
    stride : float
      Length of segment
    nfft : float
      Length of the FFT used, if a zero padded FFT is desired.
    overlap : float
      Length of overlapping segment
    cmap : str
      Colormap
    scale : str
      Plotted frequency scale. Default is "log".
    station : str
      Name of the station.
    dy : float
      Half the difference between the maximum and minimum magnetic field
      values to be plotted. This can be used if multiple figures are made
      from different stations such that the plotted range of the time series
      is of the same size for every station.
    xmin : float
      Minimum value in the power spectral density plot
    xmax : float
      Maximum value in the power spectral density plot
    funit : strg
      Frequency unit, Hz or mHz. Default is Hz.
    tunit : str
      Time unit, secs, mins or hrs. Default is mins.
    fname : str
      Output file name.
    
    Notes
    -----
    The `matplotlib.pyplot.imshow <https://matplotlib.org/api/pyplot_api.html?highlight=matplotlib%20pyplot%20imshow#matplotlib.pyplot.imshow>`_ module is
    used to plot the wavelet spectrogram. This module is usually used
    to plot raw images and assumes that the position of the cell in the
    input spectrogram array directly represents the position of the pixel
    in the raw image. That is, for an input Python array (in which rows
    are appended below previous ones), the first row in the array is
    assumed to represent the top line of pixel in the image. Therefore,
    in order to plot the spectrogram array using the imshow module, one
    needs to carefully check that the rows (which are representative of
    the frequency bands), are stored in descending order such that the
    lowest frequency is placed at the end (bottom) of the array.
    """
    if mode=='wavelet' and scale=='linear':
        print 'Warning: Wavelet mode chosen. Scale will be changed to log.'
        scale = 'log'
    # Initialise figure
    fig = plt.figure(figsize=(24,14),frameon=False)
    plt.subplots_adjust(left=0.07, right=0.95, bottom=0.1, top=0.95, hspace=0, wspace=0)
    if station!=None: fig.suptitle(station)
    ax1 = fig.add_axes([0.20,0.75,0.683,0.20])
    ax2 = fig.add_axes([0.20,0.10,0.683,0.64], sharex=ax1)
    ax3 = fig.add_axes([0.07,0.10,0.123,0.64])
    ax4 = fig.add_axes([0.89,0.10,0.030,0.64])
    # Prepare timing range
    tmin = data.times[0].value  if tmin==None else tmin
    tmax = data.times[-1].value if tmax==None else tmax
    mask = (data.times.value>=tmin) & (data.times.value<=tmax)
    scale_factor = 3600. if tunit=='hrs' else 60. if tunit=='mins' else 1
    times = (data[mask].times.value-tmin)/scale_factor
    # Plot time series
    if dy==None:
        ax1.plot(times,data[mask].value,alpha=0.5)
    else:
        ax1.plot(times,data[mask].value-numpy.mean(data[mask].value),alpha=0.5)
        ax1.set_ylim(-dy/2,dy/2)
    ax1.set_ylabel('Magnetic Fields [uT]',fontsize=11)
    ax1.tick_params(bottom='off',labelbottom='off')
    ax1.set_xlim(0,(tmax-tmin)/scale_factor)
    ax1.grid(b=True, which='major', alpha=0.7, ls='--')
    if mode=='wavelet':
        # Calculate wavelet parameters
        scales = mlpy.wavelet.autoscales(N=len(data[mask].value),dt=dt,dj=dj,wf=fct,p=omega0)
        spec = mlpy.wavelet.cwt(data[mask].value,dt=dt,scales=scales,wf=fct,p=omega0)
        freq = (omega0 + numpy.sqrt(2.0 + omega0 ** 2)) / (4 * numpy.pi * scales[1:])
        freq = freq * 1000. if funit=='mHz' else freq
        spec = numpy.abs(spec)**2
        spec = spec[::-1]
        # Define minimum and maximum frequencies
        fmin_log,fmax_log = min(freq),max(freq)
        fmin_linear,fmax_linear = min(freq),max(freq)
        if fmin!=None:
            log_ratio = (numpy.log10(fmin)-numpy.log10(min(freq)))/(numpy.log10(max(freq))-numpy.log10(min(freq)))
            fmin_linear = min(freq)+log_ratio*(max(freq)-min(freq))
            fmin_log = fmin
        if fmax!=None:
            log_ratio = (numpy.log10(fmax)-numpy.log10(min(freq)))/(numpy.log10(max(freq))-numpy.log10(min(freq)))
            fmax_linear = min(freq)+log_ratio*(max(freq)-min(freq))
            fmax_log = fmax
        # Get minimum and maximum amplitude in selected frequency range
        idx = numpy.where(numpy.logical_and(fmin_log<freq[::-1],freq[::-1]<fmax_log))[0]
	vmin = vmin if vmin!=None else numpy.sort(numpy.unique(spec[idx]))[1]
        vmax = spec[idx].max() if vmax==None else vmax
        # Plot spectrogram
        img = ax2.imshow(spec,extent=[times[0],times[-1],freq[-1],freq[0]],aspect='auto',
                        interpolation='nearest',cmap=cmap,norm=matplotlib.colors.LogNorm(vmin,vmax)) 
        ax2.set_xlabel('Time [%s] from %s UTC'%(tunit,from_gps(tmin)),fontsize=15)
        ax2.set_xlim(0,(tmax-tmin)/scale_factor)
        ax2.set_yscale('linear')
        ax2.set_ylim(fmin_linear,fmax_linear)
        ax2.grid(False)
        # Set up axis range for spectrogram
        twin_ax = ax2.twinx()
        twin_ax.set_yscale('log')
        twin_ax.set_xlim(0,(tmax-tmin)/scale_factor)
        twin_ax.set_ylim(fmin_log,fmax_log)
        twin_ax.spines['top'].set_visible(False)
        twin_ax.spines['right'].set_visible(False)
        twin_ax.spines['bottom'].set_visible(False)
        ax2.tick_params(which='both', labelleft=False, left=False)
        twin_ax.tick_params(which='both', labelleft=False,left=False, labelright=False, right=False)
        twin_ax.grid(False)
    if mode=='fourier':
        freq, times, spec = signal.spectrogram(data[mask],fs=data.sample_rate.value,nfft=nfft,nperseg=stride,noverlap=overlap)
        # Convert time array into minute unit
        times = (numpy.linspace(data[mask].times.value[0],data[mask].times.value[-1],len(times))-tmin)/scale_factor
        # Define minimum and maximum frequencies
        freq = freq * 1000. if funit=='mHz' else freq
        fmin = freq[1]      if fmin==None    else fmin
        fmax = max(freq)    if fmax==None    else fmax
        fmin_log,fmax_log = fmin,fmax
        # Get minimum and maximum amplitude in selected frequency range
        idx = numpy.where(numpy.logical_and(fmin<=freq,freq<=fmax))[0]
        vmin = vmin if vmin!=None else numpy.sort(numpy.unique(spec[idx]))[1]
        vmax = spec[idx].max() if vmax==None else vmax
        # Plot spectrogram
        img = ax2.pcolormesh(times,freq,spec,cmap=cmap,norm=matplotlib.colors.LogNorm(vmin,vmax))
        ax2.set_xlabel('Time [%s] from %s UTC'%(tunit,from_gps(tmin)),fontsize=15)
        ax2.set_xlim(0,(tmax-tmin)/scale_factor)
        ax2.set_ylim(fmin,fmax)
        ax2.set_yscale(scale)
        ax2.set_ylabel('Frequency [%s]'%funit,fontsize=15,labelpad=40)
        ax2.tick_params(which='both', labelleft=False, left=False)
        ax2.grid(False)
    # Calculate Power Spectral Density
    N = len(data[mask].value)
    delta_t = 1/data.sample_rate.value
    delta_f = 1. / (N * delta_t)
    f = delta_f * numpy.arange(N / 2)
    f = f * 1000. if funit=='mHz' else f
    PSD = abs(delta_t * fftpack.fft(data[mask].value)[:N / 2]) ** 2
    psd = numpy.vstack((f,PSD)).T
    # Plot Power Spectral Density
    imin = abs(psd[:,0]-fmin_log).argmin()
    imax = abs(psd[:,0]-fmax_log).argmin()
    min_power = min(psd[imin:imax,1]) if xmin==None else xmin
    max_power = max(psd[imin:imax,1]) if xmax==None else xmax
    ticks = matplotlib.ticker.FuncFormatter(lambda v,_:("$10^{%.0f}$"%math.log(v,10)))
    ax3.loglog(psd[:,1],psd[:,0],alpha=0.5)
    ax3.invert_xaxis()
    ax3.set_xlim(min_power,max_power)
    ax3.set_ylim(fmin_log,fmax_log)
    ax3.set_yscale(scale)
    ax3.set_ylabel('Frequency [%s]'%funit,fontsize=15)
    ax3.set_xlabel('PSD',fontsize=15)
    ax3.grid(b=True, which='major', alpha=0.7, ls='--')
    # Add color bar and save figure
    cb = fig.colorbar(img,cax=ax4)
    cb.set_ticks(LogLocator())
    cb.set_clim(vmin,vmax)
    ax4.set_ylabel('Power $|\mathrm{W}_v|^2$ $[\mu T^2/\mathrm{Hz}]$',fontsize=15)
    plt.show() if fname==None else plt.savefig(fname)
    plt.close(fig)

def plot_psd(data,fname=None):
    # Calculate Power Spectral Density
    N = len(data.value)
    delta_t = 1/data.sample_rate.value
    delta_f = 1. / (N * delta_t)
    f = delta_f * numpy.arange(N / 2)
    PSD = abs(delta_t * fftpack.fft(data.value)[:N / 2]) ** 2
    psd = numpy.vstack((f,PSD)).T
    # Plot Power Spectral Density
    fig = plt.figure(figsize=(14,7),frameon=False)
    plt.subplots_adjust(left=0.07, right=0.95, bottom=0.1, top=0.95, hspace=0, wspace=0)
    plt.loglog(psd[:,0],psd[:,1],alpha=0.5)
    plt.xlabel('Frequency [Hz]',fontsize=15)
    plt.ylabel('PSD',fontsize=15)
    plt.grid(b=True, which='major', alpha=0.7, ls='--')
    plt.show() if fname==None else plt.savefig(fname)
    plt.close(fig)
