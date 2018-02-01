
import os,re,json 
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

from . import system
from . import log 
#import ditio
#package_site_dir = "%s/site" % os.path.dirname(os.path.abspath(ditio.__file__))

#os.system("cp -dpR %s/*  %s" % (package_site_dir, site_name))



def new(params):
    site_name = params[0] 

    system.create_dir(site_name)
    system.create_dir( "%s/assets" % site_name)
    system.create_dir( "%s/images" % site_name)
    system.create_dir( "%s/content" % site_name)

    #import ditio
    #package_site_dir = "%s/site" % os.path.dirname(os.path.abspath(ditio.__file__))
    #os.system("cp -dpR %s/*  %s" % (package_site_dir, site_name))
    package_site_dir = '/home/sven/0/_sdks/python/sven-2.7/local/lib/python2.7/site-packages/ditio-0.0.1-py2.7.egg/ditio/site'
    system.copy(package_site_dir,site_name) 


def server(params,options):
    site_name= params[0]

    port = int(options["port"]) 
    server_address=(options["address"],port)
    httpd = BaseHTTPServer.HTTPServer(server_address, SimpleHTTPRequestHandler)
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    os.chdir(site_name) 
    httpd.serve_forever()

def index(params):
    site_name= params[0]
    property_matcher = re.compile("^([a-z\-]+\:.*)$")
    index = []
    for entry in os.listdir( "%s/content" %  site_name  ):
        if entry.find(".md") <  0: 
            continue 
        full_path = "%s/content/%s" % (site_name,entry) 
        properties = {} 
        with open(full_path) as f:
            for line in f:
                prop = property_matcher.findall(line) 
                if len(prop) < 1:
                    break 
                k,v = prop[0].split(":",1) 
                properties[k.strip()]=v.strip() 

            limit = 3
            preview_text=""
            for line in f: 
                if line.strip()=="":
                    continue 
                if line[0] == '#':
                    continue
                if line.find(".png") > -1:
                    continue 
                if line.find("```") > -1:
                    break 
                limit = limit -1 
                preview_text = preview_text + " " + line.strip() 

                if limit == 0:
                    break 
        properties.update({"file": entry.replace(".md","")})
        properties.update({"assets": " i am the assets  " })
        if "title" not in properties: 
            properties.update({"title": properties["doc-title"]  })
        properties.update({"preview": preview_text  })
        log("* markdown: %s " % entry)  
        index.append(properties) 
   

#[{"assets": "config.json,bin,setup.py,pkg_readme", "package": "pkg_readme", "title": "Getting Started", "file": "dit_getting_started", "date": "2018-01-06 14:47:41.416816", "preview": " \n Markdown is a lightweight markup language for writing documents. It is lightweight, elegant and effective.  Dittio.  Is a markdown publishing system which generates a static blog from markdown documents and jupyter noteboks. \n \n \n", "name": "dit_getting_started"}, {"assets": "config.json,bin,setup.py,krt_getting_started", "package": "krt_getting_started", "title": "Getting Started",    
    with open("%s/content/%s" % (site_name,"index.json"),'w' ) as f :
        f.write(json.dumps(index))

