
import lxml.builder

class ElementMaker(lxml.builder.ElementMaker):
    """Our ElementMaker unpacks lists when it is called, enabling it to work with 
    nested-list-returning XT transformations.
    """
    
    def __call__(self, tag, *children, **attrib):
        chs = []
        for ch in children:
            if type(ch)==list:
                for c in ch:
                    if c is not None:
                        chs.append(c)
            elif ch is not None:
                chs.append(ch)
        return lxml.builder.ElementMaker.__call__(self, tag, *chs, **attrib)

