
import html, logging, os, subprocess, sys, tempfile, time
from lxml import etree
from bl.dict import Dict
from bl.string import String

from .xml import XML
from . import JARS

log = logging.getLogger(__name__)

XSL_NAMESPACE = "xmlns:xsl='http://www.w3.org/1999/XSL/Transform'"
XSL_TEMPLATE = """<xsl:stylesheet version="1.0" %s%s><xsl:output method="xml"/></xsl:stylesheet>"""

class XSLT(XML):
    """class for holding, manipulating, and using XSL documents"""

    NS = {'xsl': 'http://www.w3.org/1999/XSL/Transform'}
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %Z"       # format for timestamp params

    CACHE = Dict()              # XSLT.CACHE = application-level cache. 
                                # The keys are digests of the XSLT text, which ensures that 
                                # unchanged xslt will cache, while changed xslt will compile.
    
    def __init__(self, cache=True, **kwargs):
        XML.__init__(self, **kwargs)
        self.__xslt = self.make_xslt(cache=cache)
        
    def __call__(self, elem, **params):
        # prepare string parameters -- see http://lxml.de/xpathxslt.html#stylesheet-parameters
        if 'timestamp' not in params.keys():     # always include a timestamp param
            params['timestamp'] = time.strftime(self.TIMESTAMP_FORMAT)
        for key in params:
            if type(params[key]) in [str, bytes]:
                params[key] = etree.XSLT.strparam(params[key])
        return self.__xslt(elem, **params)

    def saxon6(self, elem, **params):
        """Use Saxon6 to process the element. 
        If the XSLT has a filename (fn), use that. Otherwise, make temp.
        """
        saxon6path = os.path.join(JARS, 'saxon.jar')   # saxon 6.5.5, included with jing and trang
        with tempfile.TemporaryDirectory() as tempdir:
            if self.fn is None:
                xslfn = os.path.join(tempdir, "xslt.xsl")
                self.write(fn=xslfn)
            else:
                xslfn = self.fn
            srcfn = os.path.join(tempdir, "src.xml")
            outfn = os.path.join(tempdir, "out.xml")
            XML(fn=srcfn, root=elem).write()
            cmd = ['java', '-jar', saxon6path, '-o', outfn, srcfn, xslfn] \
                + ["%s=%r" % (key, params[key]) for key in params.keys()]
            log.debug("saxon6: %r " % cmd)

            try:
                subprocess.check_output(cmd)
            except subprocess.CalledProcessError as e:
                error = html.unescape(str(e.output, 'UTF-8'))
                raise RuntimeError(error).with_traceback(sys.exc_info()[2]) from None

            if self.find(self.root, "xsl:output") is None or self.find(self.root, "xsl:output").get('method')=='xml':
                return etree.parse(outfn)
            else:
                return open(outfn, 'rb').read().decode('utf-8')


    def saxon9(self, elem, **params):
        """Use Saxon9 to process the element. 
        If the XSLT has a filename (fn), use that. Otherwise, make temp.
        Returns an lxml.etree._ElementTree (not _Element)
        """
        saxon9path = os.path.join(JARS, 'saxon9', 'saxon9he.jar')   # saxon 9
        with tempfile.TemporaryDirectory() as tempdir:
            if self.fn is None:
                xslfn = os.path.join(tempdir, "xslt.xsl")
                self.write(fn=xslfn)
            else:
                xslfn = self.fn
            srcfn = os.path.join(tempdir, "src.xml")
            outfn = os.path.join(tempdir, "out.xml")
            XML(fn=srcfn, root=elem).write()
            cmd = ['java', '-jar', saxon9path, '-o:%s' % outfn, '-s:%s' % srcfn, '-xsl:%s' % xslfn] \
                + ['%s=%s' % (key, params[key]) for key in params.keys()]
            log.debug("saxon9: %r " % cmd)
            
            try:
                subprocess.check_output(cmd)
            except subprocess.CalledProcessError as e:
                error = html.unescape(str(e.output, 'UTF-8'))
                raise RuntimeError(error).with_traceback(sys.exc_info()[2]) from None
            
            if self.find(self.root, "xsl:output") is None or self.find(self.root, "xsl:output").get('method')=='xml':
                return etree.parse(outfn)
            else:
                return open(outfn, 'rb').read().decode('utf-8')

    def append(self, s, *args):
        if type(s) == etree._Element:
            elem = s
        else:
            elem = XML.Element(s, *args)
        try:
            self.root.append(elem)
            self.xslt = self.make_xslt()
        except:
            self.root.remove(elem)
            raise

    def make_xslt(self, elem=None, cache=True):
        # parse the source file here if available, so that the XSLT knows where it is.
        if elem is None: 
            if self.fn is not None:
                elem = etree.parse(self.fn)
            else:
                elem = self.root
        if cache==True:
            digest = String(etree.tounicode(elem)).digest()
            if self.__class__.CACHE.get(digest) is not None:
                return self.__class__.CACHE.get(digest)
            xsl = self.__class__.CACHE[digest] = etree.XSLT(elem)
        else:
            xsl = etree.XSLT(elem)
        return xsl

    @classmethod
    def clear_cache(self):
        XSLT.CACHE = Dict()

    # == TEMPLATE METHODS == 
    
    @classmethod
    def stylesheet(cls, *args, namespaces=None):
        if namespaces is not None:
            nst = ' ' + ' '.join(["xmlns:%s='%s'" % (k, namespaces[k]) for k in namespaces.keys() if k is not None])
            if None in namespaces.keys():
                nst += " xmlns='%s'" % namespaces[None]
        else:
            nst = ''
        xt = XML.Element(XSL_TEMPLATE % (XSL_NAMESPACE, nst))
        for arg in [a for a in args if a is not None]:
            xt.append(arg)
        return xt

    @classmethod
    def copy_all(cls):
        return XML.Element(
            """<xsl:template match="@*|node()" %s><xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy></xsl:template>""", 
            XSL_NAMESPACE)

    @classmethod
    def copy(cls, *vals):
        elem = XML.Element("""<xsl:copy %s></xsl:copy>""", XSL_NAMESPACE)
        for val in vals:
            elem.append(val)
        return elem        

    @classmethod
    def copy_select(cls, select):
        elem = XML.Element("""<xsl:copy %s select="%s"></xsl:copy>""", XSL_NAMESPACE, select)
        for val in vals:
            elem.append(val)
        return elem

    @classmethod
    def copy_of(cls):
        return XML.Element("""<xsl:copy-of %s/>""", XSL_NAMESPACE)

    @classmethod
    def copy_of_select(cls, select):
        return XML.Element("""<xsl:copy-of %s select="%s"/>""", XSL_NAMESPACE, select)

    @classmethod
    def choose(cls, *args):
        return XML.Element("<xsl:choose %s/>", XSL_NAMESPACE, *args)

    @classmethod
    def when(cls, test, *vals):
        elem = XML.Element("""<xsl:when %s test="%s"></xsl:when>""", XSL_NAMESPACE, test)
        for val in vals:
            elem.append(val)
        return elem

    def otherwise(cls, *vals):
        elem = XML.Element("""<xsl:otherwise %s></xsl:otherwise>""", XSL_NAMESPACE, test)
        for val in vals:
            elem.append(val)
        return elem

    @classmethod
    def template_match(cls, match, *vals):
        elem = XML.Element("""<xsl:template %s match="%s"></xsl:template>""", XSL_NAMESPACE, match)
        for val in vals:
            elem.append(val)
        return elem

    @classmethod
    def template_match_mode(cls, match, mode, *vals):
        elem = XML.Element("""\n<xsl:template %s match="%s" mode="%s"></xsl:template>""", 
            XSL_NAMESPACE, match, mode)
        for val in vals:
            elem.append(val)
        return elem
                
    @classmethod
    def template_name(cls, name, *vals):
        elem = XML.Element("""<xsl:template %s name="%s"></xsl:template>""", 
            XSL_NAMESPACE, name)
        for val in vals:
            elem.append(val)
        return elem

    @classmethod
    def template_match_omission(cls, match):
        return XML.Element("""<xsl:template %s match="%s"/>""", XSL_NAMESPACE, match)

    @classmethod
    def apply_templates(cls):
        return XML.Element("""<xsl:apply-templates %s/>""", XSL_NAMESPACE)

    @classmethod
    def apply_templates_mode(cls, mode):
        return XML.Element("""<xsl:apply-templates %s mode="%s"/>""", XSL_NAMESPACE, mode)

    @classmethod
    def apply_templates_select(cls, select):
        return XML.Element("""<xsl:apply-templates %s select="%s"/>""", XSL_NAMESPACE, select)

    @classmethod
    def apply_templates_select_mode(cls, select, mode):
        return XML.Element("""<xsl:apply-templates %s select="%s" mode="%s"/>""", 
            XSL_NAMESPACE, select, mode)

    @classmethod
    def element(cls, name, *vals):
        elem = XML.Element("""<xsl:element %s name="%s"></xsl:element>""", 
            XSL_NAMESPACE, name)
        for val in vals:
            elem.append(val)
        return elem
        
    @classmethod
    def attribute(cls, name, *vals):
        elem = XML.Element("""<xsl:attribute %s name="%s"></xsl:attribute>""", 
            XSL_NAMESPACE, name)
        for val in vals:
            elem.append(val)
        return elem

    @classmethod
    def variable(cls, name, *vals):
        elem = XML.Element("""<xsl:variable %s name="%s"></xsl:variable>""", 
            XSL_NAMESPACE, name)
        for val in vals:
            elem.append(val)
        return elem

    @classmethod
    def variable_select(cls, name, select):
        return XML.Element("""<xsl:variable %s name="%s" select="%s"/>""", 
            XSL_NAMESPACE, name, select)

    @classmethod
    def value_of(cls, select):
        return XML.Element("""<xsl:value-of %s select="%s"/>""", XSL_NAMESPACE, select)

    @classmethod
    def text(cls, t):
        return XML.Element("""<xsl:text %s>%s</xsl:text>""", XSL_NAMESPACE, t)

    @classmethod
    def for_each(cls, select, *vals):
        elem = XML.Element("""<xsl:for-each %s select="%s"></xsl:for-each>""", 
            XSL_NAMESPACE, select)
        for val in vals:
            elem.append(val)
        return elem

    @classmethod
    def if_test(cls, test, *vals):
        return XML.Element("""<xsl:if %s test="%s"></xsl:if>""", XSL_NAMESPACE, test)
        for val in vals:
            elem.append(val)
        return elem

    @classmethod
    def output_method(cls, method):
        return XML.Element("""<xsl:output method="%s" encoding="utf-8" %s/>""", 
            XSL_NAMESPACE, method)

    # -- STILL TO ADD: -- 
    # xsl:output, xsl:include, xsl:copy, xsl:copy-of, xsl:param, 
    # xsl:apply-templates select|match, xsl:call-template

# XPATH FUNCTIONS
def uppercase(context, elems):
    for elem in elems:
        if type(elem)==etree._ElementUnicodeResult:
            elem = elem.upper()
        else:
            elem.text = elem.text.upper()
            for ch in elem.getchildren():
                uppercase(cls, [ch])
                ch.tail = (ch.tail or '').upper()
    return elems

def lowercase(context, elems):
    for elem in elems:
        if type(elem)==etree._ElementUnicodeResult:
            elem = elem.lower()
        else:
            elem.text = elem.text.lower()
            for ch in elem.getchildren():
                lowercase(cls, [ch])
                ch.tail = (ch.tail or '').lower()
    return elems

def register_xpath_functions(functions=[], namespace=None):
    ns = etree.FunctionNamespace(namespace)
    for fn in functions:
        ns[fn.__name__] = fn

register_xpath_functions([uppercase, lowercase])

