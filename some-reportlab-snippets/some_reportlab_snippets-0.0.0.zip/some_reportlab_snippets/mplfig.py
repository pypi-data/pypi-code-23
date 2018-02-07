#!/usr/bin/env python
# encoding: utf-8
"""matplotlib_example.py
   An simple example of how to insert matplotlib generated figures
   into a ReportLab platypus document.
"""

import io
import matplotlib
# matplotlib.use('PDF')
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
    import cStringIO
    imgIO = cStringIO.StringIO
except ImportError:
    imgIO = io.BytesIO

from .flowables.pdf_image import PdfImage

###############################################################################
class PlotItem:
    def __init__(self, x, y, c = 'k', **kwargs):
        self.x = x
        self.y = y
        self.c = c
        self.k = kwargs

###############################################################################
class MatplotlibFig(object):
    def __init__(
        self, figsize = (4, 3), aspect = None, title = None, **kwargs
    ):
        self.figsize = figsize
        self.plotItems = []
        self.patchItems = []
        self.aspect = aspect
        self._xlim = None
        self._ylim = None
        self.title = title

        self.xlabel = 'x'
        self.ylabel = 'y'
        self.k = kwargs


    def addData(self, x, y, c = 'k', **kwargs):
        plotItem = PlotItem(x, y, c, **kwargs)
        self.plotItems.append(plotItem)
        

    def setData(self, x, y, c = 'k', **kwargs):
        self.plotItems = []
        plotItem = PlotItem(x, y, c, **kwargs)
        self.plotItems.append(plotItem)


    def addPatch(self, patch):
        self.patchItems.append(patch)


    @property
    def xlim(self):
        return self._xlim
        
    @xlim.setter
    def xlim(self, values):
        self._xlim = values
        
    @property
    def ylim(self):
        return self._ylim
        
    @ylim.setter
    def ylim(self, values):
        self._ylim = values


    @property
    def aspect(self):
        return self._aspect
        
    @aspect.setter
    def aspect(self, values):
        self._aspect = values

 
    def savefig(self):
        fig = plt.figure(figsize = self.figsize, **self.k)
        
        if self.title is not None:
            fig.suptitle(self.title, fontsize=14, fontweight='bold')
            
        ax = plt.subplot(111)

        for plotItem in self.plotItems:
            x = plotItem.x
            y = plotItem.y
            c = plotItem.c
            k = plotItem.k
            
            plt.plot(x, y, c, **k)

        for patchItem in self.patchItems:
            ax.add_patch(patchItem)

        if self._xlim is not None:
            plt.xlim(self._xlim)

        if self._ylim is not None:
            plt.ylim(self._ylim)

        if self._aspect is not None:
            ax.set_aspect(self._aspect)
            
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
            
        plt.tight_layout()
        # imgdata = cStringIO.StringIO()
        imgdata = imgIO()
        fig.savefig(imgdata, format = 'PDF', transparent = True)
        plt.close()
            
        myplot = PdfImage(imgdata)
        
        imgdata.close()

        return myplot
