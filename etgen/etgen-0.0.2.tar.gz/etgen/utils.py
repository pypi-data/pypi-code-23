# Copyright 2011-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.

from builtins import str
from builtins import object
from future.types import newstr
import six

def join_elems(elems, sep=' '):
    """
    Examples:
    >>> join_elems([1, 2, 3])
    [1, ' ', 2, ' ', 3]
    >>> join_elems([1, 2, 3],' / ')
    [1, ' / ', 2, ' / ', 3]
    >>> join_elems([])
    []

    """
    if not callable(sep):
        sep_value = sep

        def sep():
            return sep_value
    l = []
    s = None
    for e in elems:
        if s is not None:
            l.append(s)
        s = sep()
        l.append(e)
    return l


import datetime
from etgen import etree
from django.utils.functional import Promise
from django.utils.encoding import force_text


def pretty_print(elem):
    """Return a pretty-printed XML string for the Element.
    """
    return prettify(etree.tostring(elem, 'utf-8'))
    # the following also indented:
    # from http://renesd.blogspot.com/2007/05/pretty-print-xml-with-python.html
    # via http://broadcast.oreilly.com/2010/03/pymotw-creating-xml-documents.html
    #~ from xml.dom import minidom
    #~ rough_string = etree.tostring(elem, 'utf-8')
    #~ reparsed = minidom.parseString(rough_string)
    #~ return reparsed.toprettyxml(indent="  ")


def prettify(s):
    return s.replace('><', '>\n<')


def compatstr(s):
    """The `python-future <http://python-future.org/>`__ package
    introduces a special helper class `newstr` which simulates, under
    Python 2, the behaviour of Python 3 strings.  But
    `xml.etree.ElementTree
    <https://docs.python.org/2/library/xml.etree.elementtree.html>`__
    in Python 2 doesn't know about `python-future` and produces
    invalid XML when you feed it with such a string.

    So this function converts any `newstr` back to a real newstr.

    TODO: Not yet tested under Python 3. At the best it is just
    unefficient.

    """
    # assert_pure(s)
    if six.PY2 and isinstance(s, newstr):
        return six.text_type(s)
    return s

RESERVED_WORDS = frozenset("""
and       del       from      not       while
as        elif      global    or        with
assert    else      if        pass      yield
break     except    import    print
class     exec      in        raise
continue  finally   is        return
def       for       lambda    try
""".split())

TYPEMAP = {
    #~ datetime.datetime: py2str,
    #~ IncompleteDate : lambda e,v : str(v),
    datetime.datetime: lambda e, v: v.strftime("%Y%m%dT%H%M%S"),
    datetime.date: lambda e, v: v.strftime("%Y-%m-%d"),
    int: lambda e, v: str(v),
}


class Namespace(object):
    """An XML namespace.  Base class for
    :class:`etgen.html.HtmlNamespace` and the namespaces
    defined in :mod:`etgen.intervat`.

    """
    prefix = None
    targetNamespace = None
    names = None

    def __init__(self, targetNamespace=None, names=None, prefix=None):
        #~ if prefix is not None:
            #~ self.prefix = prefix
        #~ kw.setdefault('typemap',TYPEMAP)
        #~ kw.setdefault('makeelement',self.makeelement)
        #~ nsmap = kw.setdefault('nsmap',{})

        if prefix is not None:
            self.prefix = prefix
        if names is not None:
            self.names = names
        if targetNamespace is not None:
            self.targetNamespace = targetNamespace
        if self.targetNamespace is not None:
            #~ kw.update(namespace=self.targetNamespace)

            self._ns = '{' + self.targetNamespace + '}'
            if self.prefix is not None:
                etree.register_namespace(self.prefix, self.targetNamespace)
            #~ if prefix:
            #~ nsmap[prefix] = self.targetNamespace
        #~ if used_namespaces is not None:
            #~ self.used_namespaces = used_namespaces
        #~ if self.used_namespaces is not None:
            #~ for ns in self.used_namespaces:
                #~ nsmap[ns.prefix] = ns.targetNamespace
        #~ self._element_maker = ElementMaker(**kw)
        #~ self._source_elements = {}
        if self.names is not None:
            self.define_names(self.names)
        self.setup_namespace()

    def iselement(self, *args, **kw):
        return etree.iselement(*args, **kw)

    def setup_namespace(self):
        pass

    def tostring(self, element, *args, **kw):
        class dummy(object):
            pass
        data = []
        file = dummy()
        file.write = data.append
        if self.targetNamespace is not None:
            kw.setdefault('default_namespace', self.targetNamespace)
        etree.ElementTree(element).write(file, *args, **kw)
        return b"".join(data).decode("utf-8")

    def tostring_pretty(self, *args, **kw):
        #~ kw.setdefault('xml_declaration',False)
        #~ kw.setdefault('encoding','utf-8')
        #~ kw.update(xml_declaration=False)
        #~ kw.update(encoding='utf-8')
        s = self.tostring(*args, **kw)
        #~ return s
        #~ return minidom.parseString(s).toprettyxml(indent="  ")
        return prettify(s)

    def addns(self, tag):
        if self.targetNamespace is None or tag[0] == "{":
            return tag
        return self._ns + tag

    def makeattribs(self, **kw):
        #~ ns = self._element_maker._namespace
        #~ if ns is None: return kw
        xkw = dict()
        for k, v in list(kw.items()):
            k = getattr(self, k).args[0]  # convert iname to tagname
            xkw[self.addns(compatstr(k))] = compatstr(v)
        return xkw

    def create_element(self, tag, *children, **attrib):
        nsattrib = self.makeattribs(**attrib)
        tag = self.addns(tag)
        elem = etree.Element(tag, nsattrib)
        for item in children:
            if isinstance(item, Promise):
                item = force_text(item)
                # assert_pure(item)
            if isinstance(item, dict):
                elem.attrib.update(self.makeattribs(**item))
            elif isinstance(item, six.string_types):
                # assert_pure(item)
                #~ if len(elem) and len(elem[-1]) == 0:
                if len(elem):
                    last = elem[-1]
                    last.tail = (last.tail or "") + item
                else:
                    elem.text = (elem.text or "") + item
            elif etree.iselement(item):
                elem.append(item)
            else:
                raise TypeError("bad argument: %r" % item)
            #~ print "20130805 added %s --> %s" % (item,self.tostring(elem))
        return elem

    def define_names(self, names):
        from functools import partial
        if isinstance(names, six.string_types):
            raise Exception("{} must now call itself split().".format(
                self))
        for tag in names:
            iname = tag.replace("-", "_")
            iname = iname.replace(".", "_")
            #~ if iname in ('class','for','in','def'):
            if iname in RESERVED_WORDS:
                iname += "_"
            #~ setattr(self,iname,getattr(self._element_maker,name))
            p = partial(self.create_element, tag)
            setattr(self, iname, p)

    def getnsattr(self, elem, name):
        #~ if self.targetNamespace is None or name.startswith('{'):
            #~ return elem.get(name)
        return elem.get(self._element_maker._namespace + name)

    #~ def update_attribs(self,root,**kw):
    def update(self, root, **kw):
        root.attrib.update(self.makeattribs(**kw))

    def add_child(self, parent, _name, *args, **kw):
        ecl = getattr(self, _name)
        #~ kw = self.makeattribs(**kw)
        #~ print 20120420, kw
        e = ecl(*args, **kw)
        parent.append(e)
        return e

    def fromstring(self, s, **kwargs):
        """Build an element tree from the given XML source string.

        This just forwards to the
        :meth:`xml.etree.ElementTree.fromstring` library function.
        See the `Parsing XML
        <https://docs.python.org/2.7/library/xml.etree.elementtree.html#parsing-xml>`__
        section of the Python docs.

        """
        return etree.etree.fromstringlist([s], **kwargs)

    def raw(self, *args):
        """Parses the given string into an XML Element."""
        return RAW(*args)

RAW = etree.XML


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
