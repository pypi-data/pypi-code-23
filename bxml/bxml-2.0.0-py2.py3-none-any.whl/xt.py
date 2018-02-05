
import logging
from copy import deepcopy
from lxml import etree
from bl.dict import Dict

LOG = logging.getLogger(__file__)

class XT:
    """XML Transformations (XT)"""

    def __init__(self):
        # a list of matches to select which transformation method to apply
        self.matches = []

    def match(self, expression=None, xpath=None, namespaces=None): 
        """decorator that allows us to match by expression or by xpath for each transformation method"""
        class MatchObject(Dict):
            pass
        def _match(function):
            self.matches.append(
                MatchObject(expression=expression, xpath=xpath, function=function, namespaces=namespaces))
            def wrapper(self, *args, **params):
                return function(self, *args, **params)
            return wrapper
        return _match

    def __call__(self, elems, **params):
        """provide a consistent interface for transformations"""
        ee = [] 
        if type(elems) != list:
            elems = [elems]
        for elem in elems:
            # LOG.debug("%s %r" % (elem.tag, elem.attrib))
            if type(elem)==str:
                ee.append(elem)
            else:
                the_match = self.get_match(elem)
                if the_match is not None:
                    ee += the_match.function(elem, **params) or []
                else:
                    ee += self.omit(elem, **params)
        return [e for e in ee if e is not None]

    def get_match(self, elem):
        """for the given elem, return the @match function that will be applied"""
        for m in self.matches:
            if (m.expression is not None and eval(m.expression)==True) \
            or (m.xpath is not None and len(elem.xpath(m.xpath, namespaces=m.namespaces)) > 0):
                LOG.debug("=> match: %r" % m.expression)
                return m

    def Element(self, elem, **params):
        """Ensure that the input element is immutable by the transformation. Returns a single element."""
        res = self.__call__(deepcopy(elem), **params)
        if len(res) > 0: 
            return res[0]
        else:
            return None

    # == COMMON TRANSFORMATION METHODS ==

    def inner_xml(self, elem, with_tail=True, **params):
        x = [elem.text or ''] \
            + self(elem.getchildren(), **params)
        if with_tail == True:
            x += [elem.tail or '']
        return x

    def omit(self, elem, keep_tail=True, **params):
        r = []
        if keep_tail == True and elem.tail is not None:
            r += [elem.tail]
        return r

    def copy(self, elem, **params):
        return deepcopy(elem)

