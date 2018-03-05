'''
This module provides some extensions to matplotlib.

:references:

  * `Colormaps <http://matplotlib.org/examples/color/colormaps_reference.html>`_

:dependencies:

  * numpy
  * matplotlib

:copyright:

  | Tom de Geus
  | tom@geus.me
  | http://www.geus.me
'''

# ==================================================================================================

def copy_style():

  import os
  import matplotlib

  from pkg_resources import resource_string

  files = [
    'stylelib/goose.mplstyle',
    'stylelib/goose-latex.mplstyle',
    'stylelib/goose-tick-in.mplstyle',
    'stylelib/goose-tick-lower.mplstyle',
  ]

  for fname in files:

    text = resource_string(__name__, fname).decode()

    path = os.path.abspath(os.path.join(matplotlib.get_configdir(), fname))

    if not os.path.isdir(os.path.dirname(path)): os.makedirs(os.path.dirname(path))

    open(path,'w').write(text)

# ==================================================================================================

import matplotlib.pyplot as plt
import matplotlib        as mpl
import numpy             as np
import os,re,sys

# ==================================================================================================

def set_decade_lims(axis=None,direction=None):
  r'''
Set limits the the floor/ceil values in terms of decades.

:options:

  **axis** ([``None``] | ...)
    Specify the axis to which to apply the limits (default: ``plt.gca()``).

  **direction** ([``None``] | ``'x'`` | ``'y'``)
    Limit the application to a certain direction (default: both).
  '''

  # get current axis
  if axis is None:
    axis = plt.gca()

  # x-axis
  if direction is None or direction == 'x':
    # - get current limits
    MIN,MAX = axis.get_xlim()
    # - floor/ceil to full decades
    MIN = 10 ** ( np.floor(np.log10(MIN)) )
    MAX = 10 ** ( np.ceil (np.log10(MAX)) )
    # - apply
    axis.set_xlim([MIN,MAX])

  # y-axis
  if direction is None or direction == 'y':
    # - get current limits
    MIN,MAX = axis.get_ylim()
    # - floor/ceil to full decades
    MIN = 10 ** ( np.floor(np.log10(MIN)) )
    MAX = 10 ** ( np.ceil (np.log10(MAX)) )
    # - apply
    axis.set_ylim([MIN,MAX])

# ==================================================================================================

def scale_lim(lim,factor=1.05):
  r'''
Scale limits to be 5% wider, to have a nice plot.

:arguments:

  **lim** (``<list>`` | ``<str>``)
    The limits. May be a string "[...,...]", which is converted to a list.

:options:

  **factor** ([``1.05``] | ``<float>``)
    Scale factor.
  '''

  # convert string "[...,...]"
  if type(lim) == str: lim = eval(lim)

  # scale limits
  D       = lim[1] - lim[0]
  lim[0] -= (factor-1.)/2. * D
  lim[1] += (factor-1.)/2. * D

  return lim

# ==================================================================================================

def cdf(data,mode='continuous',**kwargs):
  '''
Plot cumulative probability density.

:arguments:

  **data** (``<numpy.ndarray>``)
    Input data, to plot the distribution for.

:options:

  **mode** ([``'continuous'``] | ``'line'`` | ``'bar'``)
    Plot modes. The data is binned, unless ``continuous`` is used.

  **ax** (``<matplotlib>``)
    Specify an axis to include to plot in. By default the current axis is used.

:barstyle:

  **facecolor** (``<str>``)
    Face color of the patch-objects.

  **edgecolor** (``<str>``)
    Edge color of the patch-objects.

  **linestyle** ([``'solid'``] | ``'dashed'`` | ``'dashdot'`` | ``'dotted'``)
    Line-style of the outline of the patch-objects.

  **linewidth** ([``1.0``] | ``<float>``)
    Line-width of the outline of the patch-objects.

:histogram:

  **density** ([``True``] | ``False``)
    If set to ``True`` the area under the curve is normalized to one.

  **bins** ([``10``] | ``<int>``)
    Number of bins.

  **range** (``<list>``) *optional*
    Lower and upper limit of the bins. If not provided, range is simply
    ``(data.min(),data.max())``. NB: values outside the range are ignored.

  **weights** (``<numpy.ndarray>``) *optional*
    Weights, of the same shape as ``data``.

:recommended options:

  **linestyle** ([``'-'``] | ``'--'`` | ``'-.'`` | ``None``)
    Line-style

  **linewidth** (``<float>``)
    Line-width (e.g. ``1.0``).

  **marker** (``<str>``)
    Marker.

.. seealso::

  * `matplotlib.patches.Rectangle
    <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Rectangle>`_.

  * `matplotlib.pyplot.plot
    <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot>`_.
  '''

  ax = kwargs.pop('ax',plt.gca())

  # plot continuous
  # ---------------

  if mode in ['continuous','c']:
    return ax.plot(np.sort(data),np.linspace(0.0,1.0,len(data)),**kwargs)

  # plot in bins
  # ------------

  histogram            = {}
  histogram['density'] = kwargs.pop('density',True)
  for key in ['bins','range','weights']:
    if key in kwargs:
      histogram[key] = kwargs.pop(key)

  # calculate histogram
  data,bin_edges = np.histogram(data,**histogram)
  data           = np.cumsum(data)
  data          /= data[-1]
  bin_edges     += np.diff(bin_edges)[0]/2.

  # plot as curve
  if mode in ['line','lines','l']:
    return ax.plot(np.cumsum(np.diff(bin_edges))+bin_edges[0]-np.diff(bin_edges)[0]/2.,data,**kwargs)

  # plot as bars
  if mode in ['bars','bar','b']:
    for i,(x0,dx,dy) in enumerate(zip(bin_edges[:-1],bin_edges[1:]-bin_edges[:-1],data)):
      ax.add_patch(mpl.patches.Rectangle((x0,0),dx,dy,**kwargs))

  return None

# ==================================================================================================

def pdf(data,bin_edges=None,bar_plot=False,**kwargs):
  r'''
Plot probability density.

:arguments:

  **data** (``<numpy.ndarray>``)
    Data for which the probability density is plotted.

  **density** ([``True``] | ``False``)
    If set to ``True`` the area under the curve is normalized to one.

  **area** ([``1.0``] | ``<float>``)
    Normalize to a specific area.

  **bins** ([``10``] | ``<int>``)
    Number of bins.

  **range** (``<list>``) *optional*
    Lower and upper limit of the bins. If not provided, range is simply
    ``(data.min(),data.max())``. NB: values outside the range are ignored.

  **weights** (``<numpy.ndarray>``) *optional*
    Weights, of the same shape as ``data``.


:options:

  **bin_edges** ([``None``] | ``<numpy.ndarray>``)
    Specify the bin-edges. If this is specified the histogram is not calculated,
    this function is then only used from plotting.

  **bar_plot** ([``False``] | ``True``)
    If set to ``True`` a bar plot is made, see "barstyle" for options.

  **return_data** ([``False``] | ``True``)
    Set to ``True`` to output the data-points.

  **plot** ([``True``] | ``False``)
    If set to ``False`` only the data is outputted.

:plot options:

  **linestyle** ([``'-'``] | ``'--'`` | ``'-.'`` | ``None``)
    Line-style. No line is plotted if set to ``None``.

  **alpha** (``<float>``)
    Alpha of the area under the curve. If not specified the area under the
    under the curve is not plotted.

:barstyle:

  **facecolor** (``<str>``)
    Face color of the patch-objects.

  **edgecolor** (``<str>``)
    Edge color of the patch-objects.

  **linestyle** ([``'solid'``] | ``'dashed'`` | ``'dashdot'`` | ``'dotted'``)
    Line-style of the outline the patch-objects.

  **linewidth** ([``1.0``] | ``<float>``)
    Line-width of the outline the patch-objects.

:returns:

  **handle** (``<matplotlib>``), *only if ``plot==True``*
    Handle of the plot::

      handle_fill                # if 'linestyle==None'
      handle_plot                # if 'alpha==None'
      (handle_fill,handle_plot)  # otherwise

  **x,y** (``<numpy.ndarray>``), *only if ``return_data==True``*
    The data_points.


.. seealso::

  * `numpy.histogram
    <http://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.histogram.html>`_.

  * `matplotlib.patches.Rectangle
    <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Rectangle>`_.

  '''

  # define histogram
  # ----------------

  # read/default options
  area        = kwargs.pop('area'       ,1.0  )
  return_data = kwargs.pop('return_data',False)
  kwargs.setdefault(       'plot'       ,True )

  # histogram options: for input or defaults
  histogram            = {}
  histogram['density'] = kwargs.pop('density',True)
  for key in ['bins','range','weights']:
    if key in kwargs:
      histogram[key] = kwargs.pop(key)

  # calculate histogram, normalize the area
  if bin_edges is None:
    data,bin_edges = np.histogram(data,**histogram)
    data          *= area

  # convert the x- and y-axis
  x = np.cumsum(np.diff(bin_edges))+bin_edges[0]-np.diff(bin_edges)[0]/2.
  y = data

  # plot as curve
  # -------------

  if not bar_plot:

    # initiate both plot types as False
    line_plot = False
    fill_plot = False
    # initiate options that should be removed for the different plot-types
    line_rm   = ['plot','alpha']
    fill_rm   = ['plot'        ]

    # set default linestyle
    kwargs.setdefault('linestyle','-')

    # check to plot line: set options
    if kwargs['linestyle'] in ['-','--','-.',':']:
      line_plot = True
      line_args = {key:val for key,val in kwargs.items() if key not in line_rm}
      fill_rm  += ['linestyle','linewidth','label','dashes']

    # check to plot fill: set options
    if 'alpha' in kwargs:
      fill_plot = True
      fill_args = {key:val for key,val in kwargs.items() if key not in fill_rm}

    # plot background
    if fill_plot and kwargs['plot']:
      xf = np.array(x,copy=True)
      yf = np.array(y,copy=True)
      xf = np.hstack(( xf[0]*np.ones ((1)) , xf , xf[-1]*np.ones ((1)) ))
      yf = np.hstack((       np.zeros((1)) , yf ,        np.zeros((1)) ))
      hf = plt.fill(xf,yf,**fill_args)

    # plot line
    if line_plot and kwargs['plot']:
      hp = plt.plot(x,y,**line_args)

    # set handles
    if kwargs['plot']:
      if   line_plot and fill_plot: handle = (hp,hf)
      elif line_plot              : handle =  hp
      elif fill_plot              : handle =  hf
      else: raise IOError('Insufficient settings to plot, specify "linestyle" and/or "alpha" ')

    # return handles, etc.
    if   not return_data: return  handle
    elif kwargs['plot'] : return (handle,x,y)
    else                : return (       x,y)

  # plot as bars
  # ------------

  kwargs.pop('plot',False)

  for i,(x0,dx,dy) in enumerate(zip(bin_edges[:-1],bin_edges[1:]-bin_edges[:-1],data)):
    plt.gca().add_patch(mpl.patches.Rectangle((x0,0),dx,dy,**kwargs))

  return (x,y)

# ==================================================================================================

def patch(*args,**kwargs):
  '''
Add patches to plot. The color of the patches is indexed according to a specified color-index.

:example:

  Plot a finite element mesh: the outline of the undeformed configuration, and the deformed
  configuration for which the elements get a color e.g. based on stress::

    import matplotlib.pyplot as plt
    import goosempl          as gplt

    fig,ax = plt.subplots()

    p = gplt.patch(coor=coor+disp,conn=conn,ax=ax,cindex=stress,cmap='YlOrRd',edgecolor=None)
    _ = gplt.patch(coor=coor     ,conn=conn,ax=ax)

    cbar = fig.colorbar(p,ax=ax,aspect=10)

    plt.show()

:arguments - option 1/2:

  **patches** (``<list>``)
    List with patch objects. Can be replaced by specifying ``coor`` and ``conn``.

:arguments - option 2/2:

  **coor** (``<numpy.ndarray>`` | ``<list>`` (nested))
    Matrix with on each row the coordinates (positions) of each node.

  **conn** (``<numpy.ndarray>`` | ``<list>`` (nested))
    Matrix with on each row the number numbers (rows in ``coor``) which form an element (patch).

:options:

  **cindex** (``<numpy.ndarray>``)
    Array with, for each patch, the value that should be indexed to a color.

  **ax** (``<matplotlib>``)
    Specify an axis to include to plot in. By default the current axis is used.

  **autoscale** ([``True``] | ``False``)
    Automatically update the limits of the plot (currently automatic limits of Collections are not
    supported by matplotlib).

:recommended options:

  **cmap** (``<str>`` | ...)
    Specify a colormap.

  **linewidth** (``<float>``)
    Width of the edges.

  **edgecolor** (``<str>`` | ...)
    Color of the edges.

  **clim** (``(<float>,<float>)``)
    Lower and upper limit of the color-axis.

:returns:

  **handle** (``<matplotlib>``)
    Handle of the patch objects.

.. seealso::

  * `matplotlib example
    <http://matplotlib.org/examples/api/patch_collection.html>`_.
  '''

  from matplotlib.collections import PatchCollection
  from matplotlib.patches     import Polygon

  # check dependent options
  if ( 'coor' not in kwargs or 'conn' not in kwargs ):
    raise IOError('Specify both "coor" and "conn"')

  # extract local options
  ax        = kwargs.pop( 'ax'        , plt.gca() )
  cindex    = kwargs.pop( 'cindex'    , None      )
  coor      = kwargs.pop( 'coor'      , None      )
  conn      = kwargs.pop( 'conn'      , None      )
  autoscale = kwargs.pop( 'autoscale' , True      )
  # set defaults
  kwargs.setdefault('edgecolor','k')

  # no color-index -> set transparent
  if cindex is None:
    kwargs.setdefault('facecolor',(0.,0.,0.,0.))

  # convert mesh -> list of Polygons
  if coor is not None and conn is not None:
    poly = []
    for iconn in conn:
      poly.append(Polygon(coor[iconn,:]))
    args = tuple(poly, *args)

  # convert patches -> matplotlib-objects
  p = PatchCollection(*args,**kwargs)
  # add colors to patches
  if cindex is not None:
    p.set_array(cindex)
  # add patches to axis
  ax.add_collection(p)

  # rescale the axes manually
  if autoscale:
    # - get limits
    xlim = [ np.min(coor[:,0]) , np.max(coor[:,0]) ]
    ylim = [ np.min(coor[:,1]) , np.max(coor[:,1]) ]
    # - set limits +/- 10% extra margin
    plt.xlim([xlim[0]-.1*(xlim[1]-xlim[0]),xlim[1]+.1*(xlim[1]-xlim[0])])
    plt.ylim([ylim[0]-.1*(ylim[1]-ylim[0]),ylim[1]+.1*(ylim[1]-ylim[0])])

  return p

# ==================================================================================================


