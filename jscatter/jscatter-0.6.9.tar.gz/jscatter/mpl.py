# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
This is a rudimentary interface to matplotlib to use dataArrays easier.
The standard way to use matplotlib is full available without using this module..

The intention is to allow fast/easy plotting (one command to plot) with some convenience function in relation to dataArrays
and in a non blocking mode of matplotlib.
E.g. to include automatically the value of an attribute in the legend::

 fig[0].Plot(mydataArray,legend='sqr=$qq ',sy=[2,3,-1],li=0)

With somehow shorter form to determine the marker (sy=symbol) and line (li)
and allow plotting in one line. Matplotlib is quite slow and looks for me ugly (really not paper ready).
For 2D plotting use xmgrace.
For 3D plotting this will give some simple plot options (planned).

* The new methods introduced all start with a big Letter to allow still the access of the original methods.
* By indexing as the axes subplots can be accessed as figure[i] which is figure.axes[i].
* Same for axes with lines figure[0][i] is figure.axes[0].lines[i].

Example 1::

    import jscatter as js
    import numpy as np
    i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
    p=js.mplot()
    p[0].Plot(i5,sy=[-1,4,-1],li=1,legend='Q= $q')
    p[0].Yaxis(scale='l')
    p[0].Title('intermediate scattering function')
    p[0].Legend()
    p[0].Yaxis(label='I(Q,t)/I(Q,0)')
    p[0].Xaxis(label='Q / 1/nm')

Example 2::

    import jscatter as js
    import numpy as np
    from matplotlib import pyplot
    # use this
    #fig=pyplot.figure(FigureClass=js.mpl.Figure)
    # or
    fig=js.mplot()
    fig.Multi(2,1)
    fig[0].SetView(0.1,0.25,0.8,0.7)
    fig[1].SetView(0.1,0.09,0.8,0.15)
    q=js.loglist(0.01,5,100)
    aa=js.dA(np.c_[q,np.sin(q),0.1*np.cos(q)].T)
    bb=js.dA(np.c_[q,q**2].T)
    bb.qq=123
    fig[0].Plot(aa,legend='sin',sy=2,li=3)
    for pp in range(10):  fig[0].Plot(aa.X,aa.Y*pp,legend='sin',sy=[-1,8,-1,''],li=0,markeredgewidth =1)
    fig[1].Plot(bb,legend='sqr=$qq ',sy=2,li=0)
    fig[0].Title('test')
    fig[0].Legend()
    fig[1].Legend()
    fig[0].Yaxis(label='y-axis')
    fig[1].Yaxis(label='Residuals')
    fig[1].Xaxis(label='x-axis')

"""
import numpy as np
from functools import reduce

import matplotlib
from matplotlib.projections import register_projection
from matplotlib import pyplot 
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm

lineStyles=('','-','--','-.',':')
linecolors=('w','k','r','b','g','c','m','y',)
fillstyles = ( 'none','full', 'left', 'right', 'bottom', 'top',)
symboldefault=[1,5,1,'']  # type,size,facecolor,edgecolor
linedefault=[1,0.5,1]    # type,size,color

#: gracefactor to get same scaling as in grace set to 10
gf=1

def _translate(axlen,kwargs,data=None):
    """
    This function transforms a short description as [1,2,3] for symbol and line to matplotlib compatible arguments.
    This allows a shorter description of the symbol and line formats.
    Additionally the replacement of $parname in dataArray attributes is done.
    
    
    """
    #split some special keywords in kwargs
    if 'legend' in kwargs:
        legend=kwargs['legend']
        del kwargs['legend']
    elif 'le' in kwargs:
        legend=kwargs['le']
        del kwargs['le']
    else:
        legend=''
    if 'line' in kwargs:
        line=kwargs['line']
        del kwargs['line']
    elif 'li' in kwargs:
        line=kwargs['li']
        del kwargs['li']
    else:
        line=''
    if 'symbol' in kwargs:
        symbol=kwargs['symbol']
        del kwargs['symbol']
    elif 'sy' in kwargs:
        symbol=kwargs['sy']
        del kwargs['sy']
    else:
        symbol=[-1,5,-1]
    if 'errorbar' in kwargs:
        errorbar=kwargs['errorbar']
        del kwargs['errorbar']
    elif 'er' in kwargs:
        errorbar=kwargs['er']
        del kwargs['er']
    else:
        errorbar=None
    #replace $attr by the value in data
    if '$' in legend and hasattr(data,'_isdataArray'):
        for par in data.attr:
            if '$'+par in legend or '$('+par+')' in legend:
                # noinspection PyBroadException
                try:
                    vall=np.array(getattr(data,par)).flatten()[0]
                    if isinstance(vall,(int,float)):
                        val='%.4g'%vall
                    else:
                        val=str(vall)
                    if '$('+par+')' in legend:
                        legend=legend.replace('$('+par+')',val)
                    else:
                        legend=legend.replace('$'+par,val)
                except:
                        pass
    #--------
    if isinstance(symbol,(int,str)):
        symbol=[symbol,5,1,''] # type,size,facecolor,edgecolor
    symbol=symbol+symboldefault[len(symbol):]
    # symbol marker
    if isinstance(symbol[0],(int,float)):
        if symbol[0]<0:symbol[0]=axlen
        if symbol[0]>0:
            symbol[0]=Line2D.filled_markers[divmod(symbol[0]-1,len(Line2D.filled_markers))[1]]
        else:
            symbol[0]=''
    # symbol color
    if isinstance(symbol[2],(int,float)):
        if symbol[2]<0:symbol[2]=axlen
        if symbol[2]>0:
            symbol[2]=linecolors[divmod(symbol[2]-1,len(linecolors)-1)[1]+1]
        else:
            symbol[2]=''
    if isinstance(symbol[3],(int,float)):
        if symbol[3]<0:symbol[3]=axlen
        if symbol[3]>0:
            symbol[3]=linecolors[divmod(symbol[3]-1,len(linecolors)-1)[1]+1]
        else:
            symbol[3]=linecolors[0]
    else:
        # synchronize with facecolor
        symbol[3]=symbol[2]
    if isinstance(line,(int,str)):
        line=[1,0.5,line] # type,size,color
    line=line+linedefault[len(line):]
    if isinstance(line[0],(int,float)): # type
        if line[0]<0:line[0]=axlen
        if line[0]>0:
            line[0]=lineStyles[divmod(line[0]-1,len(lineStyles)-1)[1]+1]
        else:
            line[0]=''
    if isinstance(line[2],(int,float)): # color
        if line[2]<0:line[2]=axlen
        if line[2]>0:
            line[2]=linecolors[divmod(line[2]-1,len(linecolors)-1)[1]+1]
        else:
            line[0]=''
            line[2]=''
        if symbol[0]=='' and line[2]!='':
            symbol[2]=line[2]
    #fmt=fmt,markersize=ssize, markerfacecolor=mfc,linewidth=lsize,label=legend
    for opt,val in zip(['fmt','markersize','markerfacecolor','markeredgecolor','linewidth','label','elinewidth'],
                       [symbol[2]+symbol[0]+line[0],symbol[1]*gf,symbol[2],symbol[3],line[1],legend,errorbar]):
        if opt not in kwargs:
            kwargs[opt]=val
    return kwargs


class paperAxes(matplotlib.axes.Axes):
    """
    An Axes that default is close to paper quality output
    
    """
    
    name='paper'
    #def __init__(self,*args,**kwargs):
    #    super(matplotlib.axes.Axes, self).__init__(*args,**kwargs)
 
    def SetView(self,xmin=None,ymin=None,xmax=None,ymax=None):
        """
        this sets the viewport coords.

        Parameters
        ----------
        xmin,xmax,ymin,ymax : float
            view range

        """
        self.set_position([xmin, ymin, xmax-xmin, ymax-ymin])   # [left, bottom, width, height]
        self.figure.show()
        
    def __getitem__(self, key):
        return self.lines[key]

    # noinspection PyIncorrectDocstring
    def Plot(self,*datasets,**kwargs):
        """
        plot dataArrays or array in matplotlib axes.
        
        Parameters
        ----------
        datasets : dataArray, dataList,numpy array, lists of them
            several of (comma separated) nonkeyword arguments or as list
            if dimension of datasets is one a new Data object is created and plotted
            see Notes below for error plots
        symbol,sy : int, list of float
            - [symbol,size,color,fillcolor,fillpattern] as [1,1,1,-1];
            - single integer to chose symbol eg symbol=3;  symbol=0 switches off
            - negative increments from last
            - symbol => see Line2D.filled_markers
            - size   =>    size in pixel
            - color  => int in sequence = wbgrcmyk
            - fillcolor=None    see color
            - fillpattern=None  0 empty, 1 full, ....test it
        line,li : int, list of float or Line object
            - [linestyle,linewidth,color] as [1,1,''];
            - negative increments
            - single integer to chose linestyle line=1; line=0 switches of
            - linestyle int   '-','--','-.',':'
            - linewidth float increasing thickness
            - color        see symbol color
        legend,le : string
            - determines legend for all datasets
            - string replacement: attr name prepended by '$' (eg. '$par')
              is replaced by value str(par1.flatten()[0]) if possible.
              $(par) for not unique names
        errorbar,er : float
            - errorbar thickness, zero is no errorbar

        """

        # concat dataList's
        if np.alltrue([hasattr(dset,'_isdataList') or (hasattr(dset,'_isdataArray') and np.ndim(dset)>1) for dset in datasets]):
            datasets=reduce(lambda a,b:a+b,datasets)
        if np.alltrue([np.ndim(dset)==1 for dset in datasets]):
            shape0=[np.shape(dset)[0] for dset in datasets]
            if shape0.count(shape0[0])==len(shape0):
                datasets=[np.asanyarray(datasets)]
        # self.lines is updated only after show so we need to count explicitly
        nlines=len(self.lines)
        showerr=True
        if 'comment' in kwargs: del kwargs['comment']
        if 'errorbar' in kwargs:
            if kwargs['errorbar']==0: showerr=False
        elif 'er' in kwargs:
            if kwargs['er']==0:       showerr=False
        for data in datasets:
            if hasattr(data,'_isdataArray'):
                if hasattr(data,'_iey') and showerr:
                    yerr=data.eY
                else:
                    yerr=None
                nkwargs=_translate(nlines+1,kwargs.copy(),data)
                self.errorbar(x=data.X,y=data.Y,yerr=yerr,**nkwargs)
                nlines+=1
            elif hasattr(data,'_isdataList'):
                for da in data:
                    if hasattr(data,'_iey') and showerr:
                        yerr=data.eY
                    else:
                        yerr=None
                    nkwargs=_translate(nlines+1,kwargs.copy(),da)
                    self.errorbar(x=da.X,y=da.Y,yerr=yerr,**nkwargs)
                    nlines+=1
            elif isinstance(data,np.ndarray):
                if showerr:
                    # noinspection PyBroadException
                    try :
                        yerr=data[2]
                    except:
                        yerr=None
                nkwargs=_translate(nlines+1,kwargs.copy())
                self.errorbar(x=data[0],y=data[1],yerr=yerr,**nkwargs)
                nlines+=1
        self.figure.show()
        
    def Yaxis(self,label=None,scale=None,min=None,max=None,**kwargs):
        """
        set Yaxis

        Parameters
        ----------
        label : string
            label
        scale : 'log', 'normal'
        min,max : float
            min and max of scale
        kwargs : kwargs of axes.set_xscale
            any given kwarg overrides the previous


        """
        if label is not None:
            self.set_ylabel(label)
        self.set_ylim(min,max)
        if scale is not None:
            if scale[0]=='l':
                val='log'
                kwargs['nonposx']='clip'
            elif  scale[0]=='n':
                val='linear'
            if 'subsy' not in kwargs:
                kwargs['subsy']=[2, 3, 4, 5, 6, 7, 8, 9]
            self.set_yscale(val,**kwargs)
        self.figure.show()
        
    def Xaxis(self,label=None,scale=None,min=None,max=None,**kwargs):
        """
        set Xaxis

        Parameters
        ----------
        label : string
            label
        scale : 'log', 'normal'
        min,max : float
            min and max of scale
        kwargs : kwargs of axes.set_xscale
            any given kwarg overrides the previous


        """
        if label is not None:
            self.set_xlabel(label)
        self.set_xlim(min,max)
        if scale is not None:
            if scale[0]=='l':
                val='log'
                kwargs['nonposx']='clip'
            elif  scale[0]=='n':
                val='linear'
            if 'subsx' not in kwargs:
                kwargs['subsx']=[2, 3, 4, 5, 6, 7, 8, 9]
            self.set_xscale(val,**kwargs)
        self.figure.show()

    def Resetlast(self,):
        pass

    def Legend(self,**kwargs):
        """
        Set axis legend; see Figure.legend
        """
        if 'charsize' in kwargs:
            kwargs['fontsize']=kwargs['charsize']*10.
            del kwargs['charsize']
        if 'fontsize' not in kwargs:kwargs['fontsize']=12
        if 'labelspacing' not in kwargs:kwargs['labelspacing']=0.2
        if 'loc' not in kwargs:kwargs['loc']=2 # upper left
        x=None
        y=None
        if'x' in kwargs :
            x=kwargs['x']
            del kwargs['x']
        if 'y' in kwargs :
            y=kwargs['y']
            del kwargs['y']
        if x is not None and y is not None: kwargs['bbox_to_anchor']=(x,y) # upper left
        self.legend(**kwargs)
        self.figure.show()

    def Title(self,title):
        """set Axes title"""
        self.set_title(title)
        self.figure.show()

    def Subtitle(self,subtitle):
        """
        Append subtitle to title
        """
        subtitle=self.get_title()+'\n'+subtitle
        self.set_title(subtitle)

    def Clear(self):
        """
        Clear content of this axes
        """
        self.clear()
        self.figure.show()

# register that it can be used as other Axes
register_projection(paperAxes)

class Figure(matplotlib.figure.Figure):
    def __init__(self, *args, **kwargs):
        for opt,val in zip(['facecolor','frameon','facecolor','edgecolor'],['w',False,'w','w']):
            if opt not in kwargs:
                kwargs[opt]=val
        matplotlib.figure.Figure.__init__(self, *args, **kwargs)
        self.add_subplot(1,1,1,projection='paper')
        lastsymbol=[0,0.5,0,0,0]
        lastline=[0,0,0,0]
        lasterror=[0,0,0,0]
        
    def Multi(self,n,m):
        """
        Creates multiple subplots on grid n,m. with projection "paperAxes".

        Subplots can be accesses as fig[i]

        """
        for ax in self.axes:self.delaxes(ax)
        nn=0
        for ni in range(n):
            for mi in range(m): 
                nn+=1
                self.add_subplot(n,m,nn,projection='paper')
        self.show()
    
    def __getitem__(self, key):
        return self.axes[key]
    
    def Clear(self):
        """
        Clear content of all axes

        to clear axes use fig.clear()
        """
        for ax in self:
            ax.clear()
        self.show()

    def Save(self,filename,format,size,dpi):
        """
        Save with filename
        """
        self.savefig(filename)

    def is_open(self):
        """
        Is the figure window still open.
        """
        return pyplot.fignum_exists(self.number)

    def Exit(self):
        pass

    def Close(self):
        """
        Close the figure
        """
        pyplot.close(self)
   
def mplot():
    """
    Open matplotlib figure in interactive mode.

    Returns
    -------
    pyplot figure

    Notes
    -----
     - By indexing as the axes subplots can be accessed as figure[i] which is figure.axes[i].
     - Same for axes with lines figure[0][i] is figure.axes[0].lines[i].

    """
    pyplot.ion()
    fig=pyplot.figure(FigureClass=Figure)
    return fig

def regrid(x,y,z,xdim=None):
    """
    Make a meshgrid from XYZ data columns.

    Parameters
    ----------
    x,y,z : arary like
        Array like data should be quadratic or rectangular.
    xdim : None, shape of first x dimension
        If None the number of unique values in x is used as first dimension

    Returns
    -------
        2dim arrays for x,y,z

    """
    if xdim is None:
        xdim = len(np.unique(x))
    try:xx = x.reshape(xdim,-1)
    except:xx=None
    try:yy = y.reshape(xdim, -1)
    except:yy=None
    try:zz = z.reshape(xdim, -1)
    except:zz=None
    return xx,yy,zz

def surface(x,y,z,xdim=None,levels=8, colorMap='jet',lineMap=None,alpha=0.7):
    """
    Surface plot of x,y,z, data

    Parameters
    ----------
    x,y,z : array
        Data as array
    xdim : integer
        First dimension of x
    levels : integer, array
        Levels for contour lines as number of levels or array of specific values.
    colorMap : string
        Color map name, see showColors.
    lineMap : string
        Color name for contour lines
            b: blue
            g: green
            r: red
            c: cyan
            m: magenta
            y: yellow
            k: black
            w: white
    alpha : float [0,1], default 0.7
        Transparency of surface

    Returns
    -------
        figure

    """
    if np.ndim(x)<2:
        X,Y,Z=regrid(x,y,z,xdim)
    cmap = pyplot.get_cmap(colorMap)
    try:
        lmap = pyplot.get_cmap(lineMap)
    except ValueError:
        lmap=lineMap

    fig = pyplot.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf=ax.plot_surface(X, Y, Z,cmap=cmap,linewidth=1, antialiased=True,alpha=alpha)
    try:
        contour=ax.contour3D(X,Y,Z,levels,linewidths=1,cmap=lmap)
    except:
        contour = ax.contour3D(X, Y, Z, levels, linewidths=1, colors=lmap)

    ax.set_xlim([min(x),max(x)])
    ax.set_ylim([min(y),max(y)])
    ax.set_zlim([min(z),max(z)])
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    fig.colorbar(surf,shrink=0.8) # note that colorbar is a method of the figure, not the axes
    pyplot.tight_layout()
    pyplot.show(block=False)
    return fig

def scatter3d(x,y,z, pointsize=3, color='k'):
    """
    Scatter plot of X,Y,Z data

    Parameters
    ----------
    x,y,z : arrays
        Data
    pointsize : float
        Size of points
    color : string
        Colors for points

    Returns
    -------
        figure

    """

    #cmap = pyplot.get_cmap(colorMap)
    fig = pyplot.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc=ax.scatter(x, y, z, s=pointsize, color=color)
    mi = np.min([x,y,z])
    ma = np.max([x, y, z])
    ax.set_xlim(mi,ma)
    ax.set_ylim(mi,ma)
    ax.set_zlim(mi,ma)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_aspect("equal")
    pyplot.tight_layout()
    #fig.colorbar(scatter ,shrink=0.8) # note that colorbar is a method of the figure, not the axes
    pyplot.show(block=False)
    return fig

def contourImage(x,y,z,xdim=None,levels=8,fontsize=8,colorMap='jet',lineMap=None):
    """
    Image with contour lines of x,y,z arrays with ndim=1 or 2.

    Parameters
    ----------
    x,y,z : arrays
        x,y,z coordinates for z display
    xdim : int
        If x,y,z are one dimensional xdim is dimension of first axis of x,y,z
        If None the number of unique values in x is used
    levels : in, sequence of values
        Number of contour lines between min and max or sequence of specific values.
    colorMap : string
        Get a colormap instance from name.
        Standard mpl colormap name (see Notes).
    lineMap : string
        Label color
        Colormap name as in colorMap, otherwise as cs in in Axes.clabel
        * if None, the color of each label matches the color of the corresponding contour
        * if one string color, e.g., colors = ‘r’ or colors = ‘red’, all labels will be plotted in this color
        * if a tuple of matplotlib color args (string, float, rgb, etc), different labels will be plotted in different colors in the order specified
    fontsize : int
        Size of line labels in pixel


    Returns
    -------
        figure

    Notes
    -----
    Colormaps Names
     Accent, Accent_r, Blues, Blues_r, BrBG, BrBG_r, BuGn, BuGn_r, BuPu, BuPu_r,
     CMRmap, CMRmap_r, Dark2, Dark2_r, GnBu, GnBu_r, Greens, Greens_r, Greys,
     Greys_r, OrRd, OrRd_r, Oranges, Oranges_r, PRGn, PRGn_r, Paired, Paired_r,
     Pastel1, Pastel1_r, Pastel2, Pastel2_r, PiYG, PiYG_r, PuBu, PuBuGn,
     PuBuGn_r, PuBu_r, PuOr, PuOr_r, PuRd, PuRd_r, Purples, Purples_r,
     RdBu, RdBu_r, RdGy, RdGy_r, RdPu, RdPu_r, RdYlBu, RdYlBu_r, RdYlGn,
     RdYlGn_r, Reds, Reds_r, Set1, Set1_r, Set2, Set2_r, Set3, Set3_r,
     Spectral, Spectral_r, Vega10, Vega10_r, Vega20, Vega20_r, Vega20b,
     Vega20b_r, Vega20c, Vega20c_r, Wistia, Wistia_r, YlGn, YlGnBu, YlGnBu_r,
     YlGn_r, YlOrBr, YlOrBr_r, YlOrRd, YlOrRd_r, afmhot, afmhot_r, autumn,
     autumn_r, binary, binary_r, bone, bone_r, brg, brg_r, bwr, bwr_r, cool,
     cool_r, coolwarm, coolwarm_r, copper, copper_r, cubehelix, cubehelix_r,
     flag, flag_r, gist_earth, gist_earth_r, gist_gray, gist_gray_r, gist_heat,
     gist_heat_r, gist_ncar, gist_ncar_r, gist_rainbow, gist_rainbow_r, gist_stern,
     gist_stern_r, gist_yarg, gist_yarg_r, gnuplot, gnuplot2, gnuplot2_r, gnuplot_r,
     gray, gray_r, hot, hot_r, hsv, hsv_r, inferno, inferno_r, jet, jet_r, magma,
     magma_r, nipy_spectral, nipy_spectral_r, ocean, ocean_r, pink, pink_r, plasma,
     plasma_r, prism, prism_r, rainbow, rainbow_r, seismic, seismic_r, spectral,
     spectral_r, spring, spring_r, summer, summer_r, tab10, tab10_r, tab20, tab20_r,
     tab20b, tab20b_r, tab20c, tab20c_r, terrain, terrain_r, viridis, viridis_r,
     winter, winter_r


    """
    if np.ndim(x)<2:
        x,y,z=regrid(x,y,z,xdim)
    cmap = pyplot.get_cmap(colorMap)
    try:
        lmap = pyplot.get_cmap(lineMap)
    except ValueError:
        lmap=lineMap

    fig = pyplot.figure()
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(z,cmap=cmap) # drawing the function
    # adding the Contour lines with labels
    try:
        im.cset = pyplot.contour(z,levels,linewidths=1,cmap=lmap)
        im.labels=pyplot.clabel(im.cset,inline=True,fmt='%1.1f',fontsize=10)
    except:
        im.cset = pyplot.contour(z,levels, linewidths=1)
        im.labels = pyplot.clabel(im.cset, inline=True, fmt='%1.1f', fontsize=fontsize,colors=lmap)
    im.set_xlabel('X axis')
    im.set_ylabel('Y axis')
    fig.colorbar(im) # note that colorbar is a method of the figure, not the axes

    pyplot.show(block=False)
    return fig

def showColors():
    """
    Get a list of the colormaps in matplotlib.

    Ignore the ones that end with '_r' because these are
    simply reversed versions of ones that don't end with '_r'

    Colormaps Names
     Accent, Accent_r, Blues, Blues_r, BrBG, BrBG_r, BuGn, BuGn_r, BuPu, BuPu_r,
     CMRmap, CMRmap_r, Dark2, Dark2_r, GnBu, GnBu_r, Greens, Greens_r, Greys,
     Greys_r, OrRd, OrRd_r, Oranges, Oranges_r, PRGn, PRGn_r, Paired, Paired_r,
     Pastel1, Pastel1_r, Pastel2, Pastel2_r, PiYG, PiYG_r, PuBu, PuBuGn,
     PuBuGn_r, PuBu_r, PuOr, PuOr_r, PuRd, PuRd_r, Purples, Purples_r,
     RdBu, RdBu_r, RdGy, RdGy_r, RdPu, RdPu_r, RdYlBu, RdYlBu_r, RdYlGn,
     RdYlGn_r, Reds, Reds_r, Set1, Set1_r, Set2, Set2_r, Set3, Set3_r,
     Spectral, Spectral_r, Vega10, Vega10_r, Vega20, Vega20_r, Vega20b,
     Vega20b_r, Vega20c, Vega20c_r, Wistia, Wistia_r, YlGn, YlGnBu, YlGnBu_r,
     YlGn_r, YlOrBr, YlOrBr_r, YlOrRd, YlOrRd_r, afmhot, afmhot_r, autumn,
     autumn_r, binary, binary_r, bone, bone_r, brg, brg_r, bwr, bwr_r, cool,
     cool_r, coolwarm, coolwarm_r, copper, copper_r, cubehelix, cubehelix_r,
     flag, flag_r, gist_earth, gist_earth_r, gist_gray, gist_gray_r, gist_heat,
     gist_heat_r, gist_ncar, gist_ncar_r, gist_rainbow, gist_rainbow_r, gist_stern,
     gist_stern_r, gist_yarg, gist_yarg_r, gnuplot, gnuplot2, gnuplot2_r, gnuplot_r,
     gray, gray_r, hot, hot_r, hsv, hsv_r, inferno, inferno_r, jet, jet_r, magma,
     magma_r, nipy_spectral, nipy_spectral_r, ocean, ocean_r, pink, pink_r, plasma,
     plasma_r, prism, prism_r, rainbow, rainbow_r, seismic, seismic_r, spectral,
     spectral_r, spring, spring_r, summer, summer_r, tab10, tab10_r, tab20, tab20_r,
     tab20b, tab20b_r, tab20c, tab20c_r, terrain, terrain_r, viridis, viridis_r,
     winter, winter_r

    From
    https://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html

    """
    a = np.linspace(0, 1, 256).reshape(1,-1)
    a = np.vstack((a,a))
    # Get a list of the colormaps in matplotlib.  Ignore the ones that end with
    # '_r' because these are simply reversed versions of ones that don't end
    # with '_r'
    maps = sorted(m for m in pyplot.cm.datad if not m.endswith("_r"))
    nmaps = len(maps) + 1
    #
    fig = pyplot.figure(figsize=(5,10))
    fig.subplots_adjust(top=0.99, bottom=0.01, left=0.2, right=0.99)
    for i,m in enumerate(maps):
        ax = pyplot.subplot(nmaps, 1, i+1)
        pyplot.axis("off")
        pyplot.imshow(a, aspect='auto', cmap=pyplot.get_cmap(m), origin='lower')
        pos = list(ax.get_position().bounds)
        fig.text(pos[0] - 0.01, pos[1], m, fontsize=10, horizontalalignment='right')
    #
    pyplot.show(block=False)

def test(keepopen=True):
    """
    A small test if this is working


    """

    import jscatter as js
    import numpy as np
    from matplotlib import pyplot
    # use this
    #fig=pyplot.figure(FigureClass=js.mpl.Figure)
    # or
    fig=js.mplot()
    fig.Multi(2,1)
    fig[0].SetView(0.1,0.25,0.8,0.9)
    fig[1].SetView(0.1,0.09,0.8,0.20)
    q=js.loglist(0.01,5,100)
    aa=js.dA(np.c_[q,np.sin(q),0.1*np.cos(q)].T)
    bb=js.dA(np.c_[q,q**2].T)
    bb.qq=123
    fig[0].Plot(aa,legend='sin',sy=2,li=3)
    for pp in range(10):  fig[0].Plot(aa.X,aa.Y*pp,legend='sin',sy=[-1,4,-1,''],li=0,markeredgewidth =1)
    fig[1].Plot(bb,legend='sqr=$qq ',sy=2,li=0)
    fig[0].Title('test')
    fig[0].Legend(x=1,y=1)
    fig[1].Legend(x=1,y=1)
    fig[0].Yaxis(label='y-axis')
    fig[1].Yaxis(label='Residuals')
    fig[1].Xaxis(label='x-axis')
    if keepopen:
        return fig
    else:
        fig.Close()

