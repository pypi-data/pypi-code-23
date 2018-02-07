# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 07:07:01 2015

@author: twagner
"""

### imports from ##############################################################
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from reportlab.lib.enums import TA_CENTER as TA_CENTER
from reportlab.lib.enums import TA_RIGHT as TA_RIGHT
from reportlab.lib.enums import TA_LEFT as TA_LEFT
from reportlab.platypus.flowables import Flowable

###############################################################################
class PdfImage(Flowable):
    """
    PdfImage wraps the first page from a PDF file as a Flowable
    which can be included into a ReportLab Platypus document.
    Based on the vectorpdf extension in rst2pdf
    (http://code.google.com/p/rst2pdf/)
    """

    def __init__(self, filename_or_object, width = None, height = None,
                 kind = 'direct'):

        # If using StringIO buffer, set pointer to begining
        if hasattr(filename_or_object, 'read'):
            filename_or_object.seek(0)
            
        page = PdfReader(filename_or_object, decompress = False).pages[0]
        self.xobj = pagexobj(page)
        self.imageWidth = width
        self.imageHeight = height
        x1, y1, x2, y2 = self.xobj.BBox

        self._w, self._h = x2 - x1, y2 - y1
        
        if not self.imageWidth:
            self.imageWidth = self._w
            
        if not self.imageHeight:
            self.imageHeight = self._h
            
        self.__ratio = float(self.imageWidth)/self.imageHeight
        
        if kind in ['direct', 'absolute'] or width == None or height == None:
            self.drawWidth = width or self.imageWidth
            self.drawHeight = height or self.imageHeight
        elif kind in ['bound', 'proportional']:
            factor = min(float(width) / self._w, float(height) / self._h)
            self.drawWidth = self._w * factor
            self.drawHeight = self._h * factor

        self.bbox = False


    def wrap(self, aW, aH):
        return self.drawWidth, self.drawHeight


    def drawOn(self, canvas, x, y, _sW = 0):
        if _sW > 0 and hasattr(self, 'hAlign'):
            a = self.hAlign

            if a in ('CENTER', 'CENTRE', TA_CENTER):
                x += 0.5*_sW
            elif a in ('RIGHT', TA_RIGHT):
                x += _sW
            elif a not in ('LEFT', TA_LEFT):
                raise ValueError("Bad hAlign value " + str(a))

        xobj = self.xobj
        xobj_name = makerl(canvas._doc, xobj)

        xscale = self.drawWidth / self._w
        yscale = self.drawHeight / self._h

        x -= xobj.BBox[0] * xscale
        y -= xobj.BBox[1] * yscale

        canvas.saveState()
        canvas.translate(x, y)
        canvas.scale(xscale, yscale)

        if self.bbox: canvas.rect(0, 0, self.imageWidth, self.imageHeight)
        
        canvas.doForm(xobj_name)
        canvas.restoreState()
