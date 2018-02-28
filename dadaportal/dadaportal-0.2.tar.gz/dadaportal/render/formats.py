import logging
import markdown, docutils.examples
import os, shutil
from html import escape as htmlescape
from . import meta, _html

logger = logging.getLogger(__name__)

MAX_WIDTH = 1200

@_html.formatter
def rst(path, fp):
    return docutils.examples.html_body(fp.read(), source_path=str(path),
                                       doctitle=False,
                                       input_encoding='utf-8')

@_html.formatter
def md(_, fp):
    return markdown.markdown(fp.read())

@_html.formatter
def md_plus(_, fp):
    parser = markdown.Markdown(extensions = [
        'markdown.extensions.tables',
        'markdown.extensions.attr_list',
    ])
    return parser.convert(fp.read())

@_html.formatter
def plain(_, fp):
    return '<pre>%s</pre>' % htmlescape(fp.read())

@_html.formatter
def raw(_, fp):
    return '<body>%s</body>' % fp.read()


try:
    from PIL import Image
except ImportError:
    logger.warning('PIL is not installed, so images will be copied rather than resized.')
    def image(inpath, outpath):
        copy(str(inpath), str(outpath))
else:
    def image(inpath, outpath):
        i = Image.open(str(inpath))
        height, width = i.size 
        ratio = min(MAX_WIDTH/width, 1)
        j = i.resize((int(height*ratio), int(width*ratio)))
        # Apparently this is safe even for PNG that doesn't have progressive.
        j.save(str(outpath), optimize=True, progressive=True)
        

def copy(inpath, outpath):
    def _fid(path):
        s = path.stat()
        return s.st_dev, s.st_ino

    if outpath.exists():
        if _fid(inpath) == _fid(outpath):
            return
        else:
            outpath.unlink()

    try:
        os.link(str(inpath), str(outpath))
    except OSError as e:
        if e.errno == 18:
            shutil.copy2(str(inpath), str(outpath))
        else:
            raise

def error404(page_path, absroot):
    if page_path.suffix in article:
        func = article[page_path.suffix].func
    else:
        func = plain.func
    with page_path.open() as fp:
        body = func(page_path, fp)
    return _html._page([], absroot.rstrip('/'), '404', None, None, body, True, False)

article = {
    '.mdwn': md,
    '.md': md,
    '.mdwn+': md_plus,
    '.md+': md_plus,
    '.rst': rst,
    '.txt': plain,
}
figure = {
    '.htm': copy,
    '.html': copy,
    '.png': image,
    '.jpeg': image,
    '.jpg': image,
}
