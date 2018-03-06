from __future__ import absolute_import
from __future__ import unicode_literals
import markdown
from markdown import Extension
from markdown.inlinepatterns import Pattern


CUSTOM_CLS_RE = r'[!]{2}(?P<text>[^|]+)[|](?P<element>[^|]+)([|](?P<class>[^|]+)){0,1}[!]{2}'


class ToroElementPatternExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns["toro-element"] = ToroElementPattern(CUSTOM_CLS_RE, md)

class ToroElementPattern(Pattern):

    def handleMatch(self, matched):
        element = matched.group("element")
        text = matched.group("text")
        cls = matched.group("class")

        elem = markdown.util.etree.Element(element)
        if cls:
            elem.set("class", cls)
        elem.text = markdown.util.AtomicString(text)
        return elem

def makeExtension(*args, **kwargs):
    return ToroElementPatternExtension(*args, **kwargs)




md = markdown.Markdown(extensions=['toro-element'])
print(md.convert('i love !!hello jerrick|kbd|mehehe!!'))