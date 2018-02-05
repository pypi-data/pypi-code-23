# XSLX object class

DEBUG = False

import os, re, sys, tempfile
from lxml import etree

from bl.dict import Dict
from bl.string import String
from bl.zip import ZIP
from bxml.xml import XML
from bxml.builder import Builder
import bxml.xt
from bl.text import Text
Element = Builder()._

class XLSX(ZIP):
    NS = Dict(
        # document namespaces, in xl/*.xml
        xl="http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        r="http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        mc="http://schemas.openxmlformats.org/markup-compatibility/2006",
        x14ac="http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac"
    )

    def tempfile(self):
        "write the docx to a named tmpfile and return the tmpfile filename"
        tf = tempfile.NamedTemporaryFile()
        tfn = tf.name
        tf.close()
        os.remove(tf.name)
        shutil.copy(self.fn, tfn)
        return tfn

    def write(self, fn=None):
        fn = fn or self.fn
        if not os.path.exists(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))
        f = open(self.fn, 'rb'); b = f.read(); f.close()
        f = open(fn, 'wb'); f.write(b); f.close()

    def transform(self, transformer, fn=None, XMLClass=None, **params):
        return self.xml(fn=fn, transformer=transformer, XMLClass=XMLClass, **params)

    def read(self, src):
        """return file data from within the docx file"""
        return self.zipfile.read(src)

    @property
    def sheets(self):
        """return the sheets of data."""
        data = Dict()
        for src in [src for src in self.zipfile.namelist() if 'xl/worksheets/' in src]:
            name = os.path.splitext(os.path.basename(src))[0]
            xml = self.xml(src)
            data[name] = xml
        return data

    def xml(self, src):
        """return the xml from the src"""
        return XML(root=self.read(src))

    def workbook_data(self):
        """return a readable XML form of the data."""
        document = XML(
            fn=os.path.splitext(self.fn)[0]+'.xml', 
            root=Element.workbook())
        shared_strings = [
            str(t.text) for t in 
            self.xml('xl/sharedStrings.xml')
                .root.xpath(".//xl:t", namespaces=self.NS)]
        for key in self.sheets.keys():
            worksheet = self.sheets[key].transform(XT, shared_strings=shared_strings)
            document.root.append(worksheet.root)
        return document

XT = bxml.xt.XT()

@bxml.xt.match(XT, "elem.tag == '{%(xl)s}worksheet'" % XLSX.NS)
def worksheet(elem, **params):
    return [Element.worksheet(XT(elem.getchildren(), **params))]

@bxml.xt.match(XT, "elem.tag == '{%(xl)s}sheetData'" % XLSX.NS)
def sheetData(elem, **params):
    return XT(elem.getchildren(), **params)

@bxml.xt.match(XT, "elem.tag == '{%(xl)s}row'" % XLSX.NS)
def row(elem, **params):
    return [Element.row(XT(elem.getchildren(), **params))]

@bxml.xt.match(XT, "elem.tag == '{%(xl)s}c'" % XLSX.NS)
def cell(elem, **params):
    shared_strings = params['shared_strings']
    cell = Element.cell(Dict(**elem.attrib))
    try:
        vtext = str(XML.find(elem, ".//xl:v/text()", namespaces=XLSX.NS) or '')
        if elem.get('t')=='s':              # shared string
            cell.text = shared_strings[int(vtext)]
        elif elem.get('t')=='str':            # formula
            cell.set('formula', XML.find(elem, "xl:f/text()", namespaces=XLSX.NS))
            cell.text = str(vtext)
        else:                               # other form of data
            cell.text = str(vtext)
    except:
        print(Dict(**elem.attrib), vtext, '--', sys.exc_info()[1])
        # raise
    return [cell]

@bxml.xt.match(XT, "True")
def omissions(elem, **params):
    return XT.omit(elem, **params)
