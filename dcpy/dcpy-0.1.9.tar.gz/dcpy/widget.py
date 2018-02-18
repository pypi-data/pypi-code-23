from os import path
from IPython.core.display import display,HTML
class initiate:
    def __init__(self, source):
        self.root = path.abspath(path.dirname(__file__))
        self.source = source
        self.html = []
        self.html.append("""<!DOCTYPE html><html><head>
                         <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/dc/2.1.9/dc.min.css">
                         <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css">
                         <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.17/d3.min.js"></script>
                         <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/crossfilter/1.3.12/crossfilter.min.js"></script>
                         <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/dc/2.1.9/dc.min.js"></script>
                         </head><body>""")
    
    def prepare(self,identifier,crossfilter):
        for element in identifier:
            self.html.append("<div id='{}'></div>".format(element))
        self.html.append("<script>")
        self.html.append("var data={};".format(self.source))
        self.html.append("var ndx=crossfilter(data);")
        self.html.append("".join(crossfilter))
    
    def chart(self,name,identifier,options):
        self.html.append("dc.{}('#{}').{};".format(name,identifier,".".join(options)))
        
    def save(self,filename="dcpy.html"):
        self.html.append("dc.renderAll()")
        self.html.append("</script></body></html>")
        fp = open(filename,"w")
        fp.write("".join(self.html))
        fp.close()
    
    def output(self,filename="dcpy.html",width=700,height=350):
        display(HTML('<iframe frameborder=0 src="{}" width="{}" height="{}"></iframe>'.format(filename,width,height)))