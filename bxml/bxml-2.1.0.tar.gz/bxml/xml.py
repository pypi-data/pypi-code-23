
import os, re, time, sys, subprocess, html, json, tempfile, traceback
from copy import deepcopy
from lxml import etree
from bl.dict import Dict
from bl.id import random_id
from bl.string import String
from bl.file import File

from .schema import Schema

class XML(File):
    ROOT_TAG = None
    NS = {}
    DEFAULT_NS = None

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ", ".join(["%s=%r" % (key, self[key]) for key in self]))

    def __init__(self, fn=None, root=None, tree=None, parser=None, encoding='UTF-8', schemas=None, NS=None, **args):

        # parent init of course
        File.__init__(self, fn=fn, root=root, parser=parser, schemas=schemas, **args)

        # assign the current class's values to self, because XML's values might have been overridden in the child class.
        self.ROOT_TAG = self.__class__.ROOT_TAG
        self.DEFAULT_NS = self.__class__.DEFAULT_NS
        if NS is not None:
            self.NS = NS
        else:
            self.NS = self.__class__.NS

        # set up the root element
        if root is None and tree is not None:
            self.root = self.tree.getroot()
        elif type(root) in [str, bytes]:
            self.root = XML.fromstring(root, parser=parser)
        elif root is not None:
            self.root = root
        elif type(fn) in [str, bytes] and os.path.isfile(fn):                   # read from fn
            tree = etree.parse(fn, parser=parser)
            self.root = tree.getroot()
            self.info = self.get_info(tree=tree)
        elif self.ROOT_TAG is not None:
            from .builder import Builder
            B = Builder(default=self.DEFAULT_NS, **self.NS)
            tag = self.tag_name(self.ROOT_TAG)
            tagns = self.tag_namespace(self.ROOT_TAG) # None if no namespace
            if tagns is not None:
                nstag = list(self.NS.keys())[list(self.NS.values()).index(tagns)]
            else:
                nstag = '_' # this is the "default" nstag for the Builder
            self.root = B[nstag](tag)
        else:
            self.root = etree.Element(String(self.__class__.__name__).identifier(camelsplit=True).lower(), nsmap=self.NS)

        # set up document info (based on tree.docinfo)
        if self.info is None:
            self.info = self.get_info(tree=tree)

    @classmethod
    def get_info(c, tree=None):
        if tree is not None:
            info = Dict(**{
                'URL': tree.docinfo.URL, 
                'doctype': tree.docinfo.doctype, 
                'encoding': tree.docinfo.encoding, 
                'externalDTD': tree.docinfo.externalDTD, 
                'internalDTD': tree.docinfo.internalDTD, 
                'public_id': tree.docinfo.public_id, 
                'system_url': tree.docinfo.system_url, 
                'root_name': tree.docinfo.root_name, 
                'standalone': tree.docinfo.standalone, 
                'xml_version': tree.docinfo.xml_version,
            })
        else:
            info = Dict()
        return info

    @classmethod
    def href_to_id(C, href):
        return String(href).identifier()

    @classmethod
    def xpath(C, node, path, namespaces=None, extensions=None, smart_strings=True, **args):
        """shortcut to Element.xpath()"""
        return node.xpath(path, namespaces=namespaces or C.NS, extensions=extensions, smart_strings=smart_strings, **args)

    @classmethod
    def find(C, node, path, namespaces=None, extensions=None, smart_strings=True, **args):
        """use Element.xpath() rather than Element.find() in order to normalize the interface"""
        xp = node.xpath(path, namespaces=namespaces or C.NS, extensions=extensions, smart_strings=smart_strings, **args)
        if len(xp) > 0:
            return xp[0]

    @classmethod
    def Builder(C):
        import bxml.builder
        return bxml.builder.Builder(default=C.DEFAULT_NS, **C.NS)

    def write(self, fn=None, root=None, encoding='UTF-8', doctype=None, canonicalized=False, 
            xml_declaration=True, pretty_print=True, with_comments=True):
        data = self.tobytes(root=root or self.root, 
                    xml_declaration=xml_declaration, pretty_print=pretty_print,
                    encoding=encoding or self.info.encoding,
                    doctype=doctype or self.info.doctype, canonicalized=canonicalized,
                    with_comments=with_comments)
        if canonicalized==True and xml_declaration==True:   # add the xml declaration
            data = ("<?xml version='1.0' encoding='%s'?>\n" % encoding).encode(encoding) + data        
        File.write(self, fn=fn or self.fn, data=data)

    def tobytes(self, root=None, encoding='UTF-8', doctype=None, canonicalized=True,
            xml_declaration=True, pretty_print=True, with_comments=True):
        """return the content of the XML document as a byte string suitable for writing"""
        if root is None: root = self.root
        if canonicalized == True:
            return self.canonicalized_bytes(root)
        else:
            return etree.tostring(root, encoding=encoding or self.info.encoding,
                doctype=doctype or self.info.doctype, 
                xml_declaration=xml_declaration, 
                pretty_print=pretty_print, 
                with_comments=with_comments)

    def __bytes__(self):
        return self.tobytes(pretty_print=True)

    def tostring(self, root=None, doctype=None, pretty_print=True):
        """return the content of the XML document as a unicode string"""
        if root is None: root = self.root
        return etree.tounicode(root, 
            doctype=doctype or self.info.doctype, 
            pretty_print=pretty_print)

    def __str__(self):
        return self.tostring(pretty_print=True)

    def __unicode__(self):
        return self.__str__()

    def digest(self, **args):
        """calculate a digest based on the hash of the article's content"""
        return String(self.canonicalized).digest(**args)

    @classmethod
    def canonicalized_bytes(Cls, elem):
        from io import BytesIO
        tree = etree.ElementTree(element=elem)
        c14n = BytesIO()
        tree.write_c14n(c14n)
        return c14n.getvalue()

    @classmethod
    def canonicalized_string(Cls, elem):
        """use this for testing -- to compare two ElementTrees"""
        return Cls.canonicalized_bytes(elem).decode('UTF-8')        

    def copy(self, elem=None):
        d = self.__class__()
        for k in self.keys():
            d[k] = self[k]
        d.root = deepcopy(self.root)
        return d

    def element(self, tag_path, **attributes):
        """given a tag in xpath form and optional attributes, find the element in self.root or return a new one."""
        xpath = tag_path
        if len(attributes) > 0:
            xpath += "[%s]" % ' '.join(["@%s='%s'" % (k, attributes[k]) for k in attributes])
        e = self.find(self.root, xpath)
        if e is None: 
            tag = tag_path.split('/')[-1].split('[')[0]
            tagname = tag.split(':')[-1]
            if ':' in tag:
                nstag = tag.split(':')[0]
                tag = "{%s}%s" % (self.NS[nstag], tagname)
            e = etree.Element(tag, **attributes)  
        return e

    @classmethod
    def Element(cls, s, *args):
        """given a string s and string *args, return an Element."""
        sargs = []
        for arg in args:
            if type(arg) == etree._Element:
                sargs.append(etree.tounicode(arg))
            else:
                sargs.append(arg)
        if type(s)==etree._Element:
            t = etree.tounicode(s)
        else:
            t = s
        if len(args)==0:
            return XML.fromstring(t)
        else:
            return XML.fromstring(t % tuple(sargs))
    
    @classmethod
    def fromstring(Class, text, parser=None, base_url=None, encoding='UTF-8'):
        if type(text)==str:
            text = text.encode(encoding)
        return etree.fromstring(text, parser=parser, base_url=base_url)

    # == VALIDATION == 
    # uses the Schema object in this module

    VALIDATORS = Dict()         # caching for validators, by tag

    def Validator(self, tag=None, schemas=None, rngfn=None, rebuild=False):
        if rngfn is None:
            tag = tag or self.root.tag
            schemas = schemas or self.schemas
            if rebuild==True or self.VALIDATORS.get(tag) is None:
                rngfn = Schema.filename(tag, schemas, ext='.rng')
                if rngfn is None or rebuild==True:          # .rnc => .rng
                    rncfn = Schema.filename(tag, schemas, ext='.rnc')
                    if rncfn is not None:                   # build the rng file
                        rngfn = Schema(rncfn).trang(ext='.rng')
        if rngfn is not None:
            self.VALIDATORS[tag] = etree.RelaxNG(etree.parse(rngfn))
        return self.VALIDATORS.get(tag)

    def assertValid(self, tag=None, schemas=None, rngfn=None, validator=None):
        validator = validator or self.Validator(tag=tag, schemas=schemas, rngfn=rngfn)
        validator.assertValid(self.root)
    
    def validate(self, tag=None, schemas=None, schemafn=None, jing=True, lxml=False, schematron=False):
        errors = []
        if jing==True:
            try:
                self.jing(tag=tag, schemas=schemas, schemafn=schemafn)
            except:
                errors += str(sys.exc_info()[1]).split('\n')
        if lxml==True:
            # this throws an uncaught error if the schema cannot be parsed.
            validator = self.Validator(tag=tag, schemas=schemas, rngfn=schemafn)
            try:
                self.assertValid(validator=validator)
            except:
                errors += [str(sys.exc_info()[1]).strip()]
        if schematron==True:
            errors += self.schematron(tag=tag, schemas=schemas, schemafn=schemafn)
        return errors

    def isValid(self, tag=None, schemas=None):
        try:
            self.assertValid(tag=tag, schemas=schemas)
            return True
        except:
            return False

    def jing(self, tag=None, schemas=None, schemafn=None, ext='.rnc'):
        """use the (included) jing library to validate the XML."""
        from . import JARS
        jingfn = os.path.join(JARS, 'jing.jar')
        tag = tag or self.root.tag
        schemas = schemas or self.schemas
        schemafn = schemafn or Schema.filename(tag, schemas, ext=ext)
        if schemafn is not None:
            cmd = ['java', '-jar', jingfn, '-c', schemafn]
            if os.path.splitext(schemafn)[-1].lower() != '.rnc':
                cmd.pop(cmd.index('-c'))
            try:
                fn = self.fn
                tempf = None
                if fn is None:
                    tempf = tempfile.NamedTemporaryFile()
                    fn = tempf.name
                    tempf.close()
                    open(fn, 'wb').write(etree.tounicode(self.root).encode('utf-8'))
                subprocess.check_output(cmd + [fn])
            except subprocess.CalledProcessError as e:
                tbtext = html.unescape(str(e.output, 'UTF-8'))
                raise RuntimeError(tbtext).with_traceback(sys.exc_info()[2]) from None

    def schematron(self, tag=None, schemas=None, schemafn=None, ext='.sch'):
        """validate the XML using Schematron; the schema might be a schematron file,
            or it might be a RelaxNG schema that contains embedded Schematron.
        """
        from . import PATH
        from .xslt import XSLT
        schematron_path = os.path.join(PATH,'schematron','trunk','schematron','code')

        # select the schema filename
        tag = tag or self.root.tag
        schemas = schemas or self.schemas
        schemafn = schemafn or Schema.filename(tag, schemas, ext=ext) \
            or Schema.filename(tag, schemas, ext='.rng') \
            or Schema.filename(tag, schemas, ext='.rnc')

        assert schemafn is not None and os.path.exists(schemafn)

        # ensure that an up-to-date Schematron schema file is available.
        schfn = File(fn=schemafn).clean_filename(ext='.sch')
        fbase, fext = os.path.splitext(schfn)
        if (not(os.path.exists(schfn)) 
            or (os.path.exists(fbase+'.rnc') 
                and File(fn=schfn).last_modified < File(fn=fbase+'.rnc').last_modified)):
            # create the Schematron file from the .rnc
            schfn = Schema(fn=fbase+'.rnc').schematron()
        elif (not(os.path.exists(schfn)) 
            or (os.path.exists(fbase+'.rng') 
                and File(fn=schfn).last_modified < File(fn=fbase+'.rng').last_modified)):
            # create the Schematron file from the .rng
            schfn = Schema(fn=fbase+'.rng').schematron()

        assert schfn is not None and os.path.exists(schfn)

        # ensure that an up-to-date Schematron XSLT file is available        
        sch_xslt_fn = schfn + '.xslt' 
        if (not os.path.exists(sch_xslt_fn)
            or File(fn=sch_xslt_fn).last_modified < File(fn=schfn).last_modified):  
            # The Schematron XSLT doesn't exist or is out-of-date, so we need to update it
            sch = XML(fn=schfn)
            sch.fn = sch_xslt_fn

            # We're using the XSLT 1.0 version of Schematron.
            # even though we use XSLT 2.0+ XPath functions -- the converter doesn't actually read the patterns.
            # (tried the XSLT 2.0 version with Saxon9HE, but Schematron assumes XSLT 1.0 compatibility,
            # which Saxon9HE doesn't support.)
            for xslfb in ['iso_dsdl_include.xsl', 'iso_abstract_expand.xsl', 'iso_svrl_for_xslt1.xsl']:
                xslt = XSLT(fn=os.path.join(schematron_path, xslfb))
                sch.root = xslt.saxon6(sch.root).getroot()
                sch.write()

            # change the XSLT version from "1.0" to "2.0". (Later we might support 3.0)
            sch.root.set('version', '2.0')
            sch.write()

        assert sch_xslt_fn is not None and os.path.exists(sch_xslt_fn)

        # validate the XML against the Schematron XSLT using Saxon 9 (XSLT 3.0 / XPath 3.1) 
        sch_xslt = XSLT(fn=sch_xslt_fn)
        report = XML(root=sch_xslt.saxon9(self.root).getroot())

        # return the errors in the report_xml as a list of errors, with line numbers
        errors = []
        for failure in report.xpath(report.root, "//svrl:failed-assert", namespaces={'svrl':"http://purl.oclc.org/dsdl/svrl"}):
            for e in self.xpath(self.root, failure.get('location')):
                errors.append("%s:%d <%s %s>: error: %s" 
                    % (self.fn, e.sourceline or -1, 
                        self.tag_name(e), " ".join(['%s="%s"' % (k,v) for k,v in e.attrib.items()]), 
                        etree.tounicode(failure, method='text').strip()))
        return errors

    # == NAMESPACE == 

    def namespace(self, elem=None):
        """return the URL, if any, for the doc root or elem, if given."""
        if elem is None: elem = self.root
        return XML.tag_namespace(elem.tag)

    @classmethod
    def tag_namespace(cls, tag):
        """return the namespace for a given tag, or '' if no namespace given"""
        md = re.match("^(?:\{([^\}]*)\})?", tag)
        return md.group(1) # None if no namespace in tag

    @classmethod
    def tag_name(cls, tag):
        """return the name of the tag, with the namespace removed"""
        if type(tag) == etree._Element:
            tag = tag.tag
        return tag.split('}')[-1]

    # == TRANSFORMATIONS == 

    def xslt(self, xslfn, elem=None, cache=True, **params):
        from .xslt import XSLT
        xt = XSLT(fn=xslfn, elem=elem, cache=cache)
        return xt(elem, **params)

    def transform(self, transformer, elem=None, fn=None, XMLClass=None, **params):
        XMLClass = XMLClass or self.__class__
        elem = elem or self.root
        fn = fn or self.fn
        x = XMLClass(root=transformer.Element(elem, xml=self, fn=fn, **params), fn=fn)
        return x

    # == AUDITING == 

    def num_words(self):
        t = etree.tounicode(self.root, method="text").strip()
        words = re.split("\s+", t)
        return len(words)

    def element_map(self, tags=None, xpath="//*", exclude_attribs=[], include_attribs=[], attrib_vals=False, hierarchy=False, minimize=False):
        """return a dict of element tags, their attribute names, and optionally attribute values, 
            in the XML document
        """
        if tags is None: tags = Dict()
        for elem in self.root.xpath(xpath):
            if elem.tag not in tags.keys(): 
                tags[elem.tag] = Dict(**{'parents': [], 'children': [], 'attributes': Dict()})
            for a in [a for a in elem.attrib.keys() 
                if (include_attribs==[] and a not in exclude_attribs)
                or (a in include_attribs)
            ]:
                # Attribute Names
                if a not in tags[elem.tag].attributes.keys(): 
                    tags[elem.tag].attributes[a] = []
                # Attribute Values
                if attrib_vals==True and elem.get(a) not in tags[elem.tag].attributes[a]:
                    tags[elem.tag].attributes[a].append(elem.get(a))
            # Hierarchy: Parents and Children
            if hierarchy==True:
                parent = elem.getparent()
                if parent is not None and parent.tag not in tags[elem.tag].parents: 
                    tags[elem.tag].parents.append(parent.tag)
                for child in elem.xpath("*"):
                    if child.tag not in tags[elem.tag].children:
                        tags[elem.tag].children.append(child.tag)
        if minimize==True:
            for tag in tags.keys():
                if tags[tag].get('parents')==[]: tags[tag].pop('parents')
                if tags[tag].get('children')==[]: tags[tag].pop('children')
                if tags[tag].get('attributes')=={}: tags[tag].pop('attributes')
                if tags[tag]=={}: tags.pop(tag)
        return tags

    # == CONVERSIONS == 

    def as_json(self, elem=None, indent=None, ignore_whitespace=True, namespaces=False):
        return json.dumps(
            self.as_dict(elem=elem, ignore_whitespace=ignore_whitespace, namespaces=namespaces), 
            indent=indent)

    def as_dict(self, elem=None, ignore_whitespace=True, namespaces=False):
        """Create a generalized dict output from this elem (default self.root).
        Rules:
            * Elements are objects with a single attribute, which is the tag name.
            * The value of the single attribute is a list. The elements of the list are:
                o a dict containing attributes
                + zero or more strings or objects. 
                    - text is represented as strings
                    - elements are represented as objects
        If ignore_whitespace==True, then whitespace-only element text and tail will be omitted.
        If namespaces==True, then include the namespaces in the element/attribute names.
        Comments and processing instructions are ignored.
        The "tail" of the root node is also ignored.
        """
        if elem is None: elem = self.root
        if namespaces == False:
            tag = re.sub("^\{[^\}]*\}", "", elem.tag)
        else:
            tag = elem.tag
        attrib = Dict(**elem.attrib)
        if namespaces == False:
            for key in attrib:
                newkey = re.sub("^\{[^\}]*\}", "", key)
                attrib[newkey] = attrib.pop(key)
        d = Dict(**{tag: [attrib]})
        if elem.text is not None and (elem.text.strip() != '' or ignore_whitespace != True): 
            d[tag].append(elem.text)
        for ch in [e for e in elem if type(e) == etree._Element]:   # *** IGNORE EVERYTHING EXCEPT ELEMENTS ***
            d[tag].append(self.as_dict(elem=ch))
            if elem.tail is not None and (elem.tail.strip() != '' or ignore_whitespace != True):
                d[tag].append(elem.tail)
        return d

    # == TREE MANIPULATIONS == 

    @classmethod
    def is_empty(c, elem, ignore_whitespace=False):
        return (len(elem.getchildren())==0 
                and ((ignore_whitespace==True and (elem.text is None or elem.text.strip()==''))
                    or elem.text in [None, '']))

    @classmethod
    def remove_if_empty(c, elem, leave_tail=True, ignore_whitespace=False):
        if c.is_empty(elem, ignore_whitespace=ignore_whitespace):
            c.remove(elem, leave_tail=leave_tail)

    @classmethod
    def replace_with_contents(c, elem):
        "removes an element and leaves its contents in its place. Namespaces supported."
        parent = elem.getparent()
        index = parent.index(elem)
        children = elem.getchildren()
        previous = elem.getprevious()
        # text
        if index==0:
            parent.text = (parent.text or '') + (elem.text or '')
        else:
            previous.tail = (previous.tail or '') + (elem.text or '')
        # children
        for child in children:
            parent.insert(index + children.index(child), child)
        # tail
        if len(children) > 0:
            last_child = children[-1]
            last_child.tail = (last_child.tail or '') + (elem.tail or '')
        else:
            if index==0:
                parent.text = (parent.text or '') + (elem.tail or '')
            else:
                previous.tail = (previous.tail or '') + (elem.tail or '')
        # elem
        parent.remove(elem)

    @classmethod
    def remove(c, elem, leave_tail=True):
        parent = elem.getparent()
        if leave_tail==True:
            if parent.index(elem)==0:
                parent.text = (parent.text or '') + (elem.tail or '')
            else:
                prev = elem.getprevious()
                prev.tail = (prev.tail or '') + (elem. tail or '')
        parent.remove(elem)

    @classmethod
    def remove_range(cls, elem, end_elem, delete_end=True):
        """delete everything from elem to end_elem, including elem.
        if delete_end==True, also including end_elem; otherwise, leave it."""
        while elem is not None and elem != end_elem \
        and end_elem not in elem.xpath("descendant::*"):
            parent = elem.getparent()
            nxt = elem.getnext()
            parent.remove(elem)
            if DEBUG==True: print(etree.tounicode(elem))
            elem = nxt
        if elem == end_elem:
            if delete_end==True:
                cls.remove(end_elem, leave_tail=True)
        elif elem is None:
            if parent.tail not in [None, '']:
                parent.tail = ''
            cls.remove_range(parent.getnext(), end_elem)
            XML.remove_if_empty(parent)
        elif end_elem in elem.xpath("descendant::*"):
            if DEBUG==True: print(elem.text)
            elem.text = ''
            cls.remove_range(elem.getchildren()[0], end_elem)
            XML.remove_if_empty(elem)
        else:
            print("LOGIC ERROR", file=sys.stderr)

    @classmethod
    def wrap_content(cls, container, wrapper):
        "wrap the content of container element with wrapper element"
        wrapper.text = (container.text or '') + (wrapper.text or '')
        container.text = ''
        for ch in container: wrapper.append(ch)
        container.insert(0, wrapper)
        return container

    @classmethod
    def tag_words_in(cls, elem, tag='w'):
        w = Dict(
            PATTERN = re.compile("([^\s]+)"),
            REPLACE = r'{%s}\1{/%s}' % (tag, tag),
            OMIT_ELEMS = [])
        def tag_words(e):
            e.text = re.sub(w.PATTERN, w.REPLACE, e.text or '')
            for ch in e:
                if ch.tag not in w.OMIT_ELEMS:
                    tag_words(ch)
                ch.tail = re.sub(w.PATTERN, w.REPLACE, ch.tail or '')
        new_elem = XML.fromstring(etree.tounicode(elem))
        tag_words(new_elem)
        s = etree.tounicode(new_elem)
        s = s.replace('{%s}' %tag, '<%s>' %tag).replace('{/%s}' %tag, '</%s>' %tag)
        new_elem = XML.fromstring(s)
        return new_elem

    @classmethod
    def merge_contiguous(C, node, xpath, namespaces=None):
        """Within a given node, merge elements that are next to each other 
        if they have the same tag and attributes.
        """
        new_node = deepcopy(node)
        elems = XML.xpath(new_node, xpath, namespaces=namespaces)
        elems.reverse()
        for elem in elems:
            next = elem.getnext()
            if elem.attrib == {}: 
                XML.replace_with_contents(elem)
            elif elem.tail in [None, ''] and next is not None \
            and elem.tag==next.tag and elem.attrib==next.attrib:
                # merge next with elem
                # -- append next.text to elem last child tail
                if len(elem.getchildren()) > 0:
                    lastch = elem.getchildren()[-1]
                    lastch.tail = (lastch.tail or '') + (next.text or '')
                else:
                    elem.text = (elem.text or '') + (next.text or '')
                # -- append next children to elem children
                for ch in next.getchildren():
                    elem.append(ch)
                # -- remove next
                XML.remove(next, leave_tail=True)
        return new_node

    # == Nesting Manipulations == 

    @classmethod
    def unnest(c, elem, ignore_whitespace=False):
        """unnest the element from its parent within doc. MUTABLE CHANGES"""
        parent = elem.getparent()
        gparent = parent.getparent()
        index = parent.index(elem)
        # put everything up to elem into a new parent element right before the current parent 
        preparent = etree.Element(parent.tag)
        preparent.text, parent.text = (parent.text or ''), ''
        for k in parent.attrib.keys(): 
            preparent.set(k, parent.get(k))
        if index > 0:
            for ch in parent.getchildren()[:index]:
                preparent.append(ch)
        gparent.insert(gparent.index(parent), preparent)
        XML.remove_if_empty(preparent, leave_tail=True, ignore_whitespace=ignore_whitespace)
        # put the element right before the current parent
        XML.remove(elem, leave_tail=True)
        gparent.insert(gparent.index(parent), elem)
        elem.tail = ''
        # if the original parent is empty, remove it
        XML.remove_if_empty(parent, leave_tail=True, ignore_whitespace=ignore_whitespace)

    @classmethod
    def interior_nesting(cls, elem1, xpath, namespaces=None):
        """for elem1 containing elements at xpath, embed elem1 inside each of those elements,
        and then remove the original elem1"""
        for elem2 in elem1.xpath(xpath, namespaces=namespaces):
            child_elem1 = etree.Element(elem1.tag)
            for k in elem1.attrib: child_elem1.set(k, elem1.get(k))
            child_elem1.text, elem2.text = elem2.text, ''
            for ch in elem2.getchildren(): child_elem1.append(ch)
            elem2.insert(0, child_elem1)
        XML.replace_with_contents(elem1)

    @classmethod
    def fragment_nesting(cls, elem1, tag2, namespaces=None):
        """for elem1 containing elements with tag2, 
        fragment elem1 into elems that are adjacent to and nested within tag2"""
        elems2 = elem1.xpath("child::%s" % tag2, namespaces=namespaces)
        while len(elems2) > 0:
            elem2 = elems2[0]
            parent2 = elem2.getparent()
            index2 = parent2.index(elem2)

            # all of elem2 has a new tag1 element embedded inside of it
            child_elem1 = etree.Element(elem1.tag)
            for k in elem1.attrib: child_elem1.set(k, elem1.get(k))
            elem2.text, child_elem1.text = '', elem2.text
            for ch in elem2.getchildren():
                child_elem1.append(ch)
            elem2.insert(0, child_elem1)

            # new_elem1 for all following children of parent2
            new_elem1 = etree.Element(elem1.tag)
            for k in elem1.attrib: new_elem1.set(k, elem1.get(k))
            new_elem1.text, elem2.tail = elem2.tail, ''
            for ch in parent2.getchildren()[index2+1:]:
                new_elem1.append(ch)

            # elem2 is placed after parent2
            parent = parent2.getparent()
            parent.insert(parent.index(parent2)+1, elem2)
            last_child = elem2

            # new_elem1 is placed after elem2
            parent.insert(parent.index(elem2)+1, new_elem1)
            new_elem1.tail, elem1.tail = elem1.tail, ''

            XML.remove_if_empty(elem1)
            XML.remove_if_empty(new_elem1)

            # repeat until all tag2 elements are unpacked from the new_elem1
            elem1 = new_elem1
            elems2 = elem1.xpath("child::%s" % tag2, namespaces=namespaces)

    @classmethod
    def split(cls, elem, tag, **namespaces):
        """Split the given elem at tag, returning a list of elements with the same attributes.
        Use XML.xpath() syntax for the tag when it has a namespace; the namespace prefix
        must exist in the **namespaces
        """

