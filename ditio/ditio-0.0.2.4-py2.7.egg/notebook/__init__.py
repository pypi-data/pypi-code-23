import os, json, copy, shutil 
import re 
from  .. import system
from  .  import markdown 
from  . import code 
from  . import language

from .language import Python,Java,Clojure,Groovy,Javascript 
protect = lambda v : copy.deepcopy(v)

def publish(params):
    notebook  = params[0]
    site_name = params[1] 
    if os.path.isdir(site_name) is False:
        system.create_dir(site_name) 

    with open(notebook) as f:
        nb_json = json.loads(f.read()) 
    #[u'source', u'cell_type', u'metadata']

    cells =  nb_json["cells"]
    meta_data= nb_json["metadata"]

    context = {"metadata":meta_data}
    context["image-folder"] = "./%s/images/" % site_name
    context["content-folder"] = "./%s/content/" % site_name 
    context["assets-folder"] = "./%s/assets/" % site_name 
    context["site-name"] = site_name 
    
    lang = meta_data["language_info"]["name"].lower()  
    if lang == "python":
        language.set(Python) 
    elif lang == "java":
        language.set(Java) 
    elif lang == "clojure": 
        language.set(Clojure) 
    else:
        raise Exception ("Unknown language: %s" % lang ) 
    
    export(protect(context),cells,site_name) 


def export(context,cells,site_name):
    indexed_cells = list(enumerate(cells))
    code_cells = [ c for index,c in indexed_cells if c["cell_type"] == 'code']
    properties = {"project":"","package":""  }
    properties.update(get_properties(code_cells[0])) 
    if len(properties) == 0:
        raise Exception("Project Info not found in the first code cell") 

    context.update({"properties":dict(properties)})


    project_path = "%s/%s" % (context["assets-folder"],properties["project"])
    package_path = "%s/%s/%s" % (context["assets-folder"],properties["project"],properties["package"])

    system.create_dir(project_path) 
    system.create_dir(package_path) 

    with open("%s/settings.json" %  project_path,'w' ) as f:
        f.write(json.dumps(properties)) 

    context.update({"package-folder":package_path, "project-folder":project_path})

    markdown.export(context,protect(indexed_cells) )
    code.export(context,protect(indexed_cells)) 

def get_properties(cell):
    lang = language.get() 
    #property_matcher = re.compile("^#([a-z,\-]+)\:")
    property_matcher = re.compile('^%s([a-z,\-]+)\:' % lang.COMMENT)
    properties = []
    for l in cell["source"]:
        print l 
        if len(property_matcher.findall(l)) < 1:
            break
        l = l.strip()
        l = l.replace(lang.COMMENT,'')
        (k,v)= l.split(":",1) 
        k = k.strip()
        v = v.strip() 
        properties.append((k,v)) 
    
    return properties 



"""
Convention: 
    #INCLDUE:  directives are comments in caps
    #metaproperty:  are values in small caps 
cells -> directives -> mutators -> apply to cell 

code cells -> 'output' produce markdown images 
code cells -> 'source' produce markdown includes formatted as code blocks 'langugae' 
code cells -> 'output' produce markdown includes formatted as code blocks console text output
"""

