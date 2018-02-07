# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 08:49:49 2015

@author: twagner
"""
import os

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus.tables import Table

###############################################################################
class Report:
    def __init__(self, **kwargs):
        moduleDir = os.path.dirname(__file__)
        self.pdfFile = os.path.join(moduleDir, "resources/logo.pdf")
        self.styleSheet = getSampleStyleSheet()
        self.setTitle('')

        for key, value in kwargs.items():
            if key == 'logo':
                self.pdfFile = value
            elif key == 'title':
                self.setTitle(value)

        self.PAGE_SIZE = A4
        self.MARGIN_SIZE = 25 * mm
        
        self.FRAME_WIDTH = self.PAGE_SIZE[0] - 2 * self.MARGIN_SIZE
        self.FRAME_HEIGHT = self.PAGE_SIZE[1] - 2 * self.MARGIN_SIZE

        self.story = []

        self.style = self.styleSheet['Normal']

        self.readLogo()
    
    def readLogo(self):
        
        # set logo
        pages = PdfReader(self.pdfFile, decompress=False).pages

        self.logo_height = 80
        self.logo_margin = 10

        self.logo = pagexobj(pages[0])
        self.pdf_width = self.logo['/BBox'][2]
        self.pdf_height = self.logo['/BBox'][3]

        self.logo_scale = self.logo_height / self.pdf_height
        self.logo_width = self.logo_scale * self.pdf_width


    def save(self, pdfdoc):
        """
        Creates PDF doc from story.
        """
        pdf_doc = BaseDocTemplate(pdfdoc, pagesize = self.PAGE_SIZE,
            leftMargin = self.MARGIN_SIZE, rightMargin = self.MARGIN_SIZE,
            topMargin = self.MARGIN_SIZE, bottomMargin = self.MARGIN_SIZE)
            
        main_frame = Frame(
            self.MARGIN_SIZE, self.MARGIN_SIZE,
            self.FRAME_WIDTH, self.FRAME_HEIGHT,
            leftPadding = 0, rightPadding = 0,
            bottomPadding = 0, topPadding = 0, id = 'main_frame')
          
        main_template = PageTemplate(id = 'main_template',
                                     onPage = self.pageSetup,
                                     frames = [main_frame])
                                     
        pdf_doc.addPageTemplates([main_template])

        full_story = []
        full_story.append(self.title)
        full_story.extend(self.story)
    
        pdf_doc.build(full_story)


    def pageSetup(self, canvas, doc):
        canvas.saveState()

        x = self.PAGE_SIZE[0] - self.logo_width - self.logo_margin
        y = self.PAGE_SIZE[1] - self.logo_height - self.logo_margin

        canvas.translate(x, y)
        canvas.scale(self.logo_scale, self.logo_scale)
        drawing = makerl(canvas, self.logo)
        canvas.doForm(drawing)
        canvas.restoreState()


    def setTitle(self, title):
        self.title = Paragraph(title, self.styleSheet['Title'])
        
###############################################################################
class User(Table):
    def __init__(self):

        str_date = '1.1.2016'
        str_time = '0:0'
        user = 'Thomas Wagner'
        
        data_user = [
            ['Datum:', str_date],
            ['Zeit:', str_time],
            ['Bearbeiter:', user],
        ]
      
        
        table_style = [
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ] 

        Table.__init__(self, data_user, repeatRows = 0)
        self.setStyle(table_style)
        self.hAlign = 'LEFT'
