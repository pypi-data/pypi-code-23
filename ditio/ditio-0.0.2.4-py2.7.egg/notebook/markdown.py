import shutil,re  
from . import __init__ 
import language 
from .. import trace, log 
from  ..  import utils 
from  ..utils  import apply_commands, commands_update 

import re 
def export(context,indexed_cells):
    # get meta data 
    markdown_cells = [] 
    for index,cell in  indexed_cells:
        commands = get_cell_commands(cell) 
        context["cell_no"] = index
        cell= apply_commands(context,markdown_mutator,commands,cell) 
        if cell["cell_type"] == "markdown": 
            markdown_cells.append(cell)

    
    md_fname = "%s/%s.md" % (context["content-folder"],context["properties"]["doc-name"])
    with open(md_fname,'w') as f:
        for k in context["properties"]:
            v = context["properties"][k] 
            f.write("%s: %s" % (k,v))
            f.write("\n") 
        
        f.write("---\n")

        for c in markdown_cells:
            f.write("\n") 
            f.write(  "\n".join([(l.encode('utf8').strip()) for l in  c["source"] ]) )

    #post process
    if "doc-image" in context["properties"]: 
        doc_image = context["properties"]["doc-image"] 
        full_path="%s/%s" % (context["image-folder"],doc_image.split("/")[-1] )
        trace("(doc-image-export): %s" % full_path ) 
        shutil.copy2(doc_image,full_path) 
        print doc_image 

def get_cell_commands(cell):
    #directive_matcher = re.compile("^#([A-Z]+)\:")
    lang = language.get() 

    directive_matcher = re.compile('^%s([A-Z]+)\:' %  lang.COMMENT)
    # set up default dirctives 
    directives = [("EXPORT_IMAGES",""),("INCLUDE",str(False))] 
    #directives = [("EXPORT_IMAGES","")] 
    for l in cell["source"]:
        matches = directive_matcher.findall(l)
        if matches == []:
            break 
        directive = matches[0] 
        params = l.split(":",1)[1].strip()
        if params == '':
            params=str(True) 
        #directives.append( (directive,params))
        commands_update(directives, directive, params)

    # add defaults 

    if cell["cell_type"] == "code": 
        for output in cell["outputs"]: 
            if output["output_type"]=='display_data':
                if "image/png" in output["data"]:
                    directives.append( ("IMAGE_EXTRACT","image/png")) 

    return directives 

def markdown_mutator(context,cell,command,params):
    if command == "EXPORT_IMAGES":
        if cell["cell_type"] == 'markdown': 
            markdown_image_matcher = re.compile(".*\!\[.*\]\((.*)\).*")
            for index,l in enumerate(cell["source"]):
                if markdown_image_matcher.match(l) is not None: 
                    for img in markdown_image_matcher.findall(l):
                        folder = context["image-folder"] 
                        fname = img.split("/")[-1] 
                        trace("* (markdown-mutator): copy %s -> %s" % (img,"%s/%s" % (folder,fname)) ) 
                        shutil.copy2(img,"%s/%s" % (folder,fname)) 
                        cell["source"][index] =  l.replace("./","/") # hacky replace for images relative urls   
    elif command == "INCLUDE":
        if cell["cell_type"] == 'code':
            if params != str(False): 
                language =  context["metadata"]["language_info"]["name"]
                lines = ["```%s\n" %  language ]
                lines.extend([l for l in   cell["source"] if l[0] !=  '#' ])
                lines.extend(['```\n'])
                cell["cell_type"] = "markdown"
                cell["source"] = lines 
            else:
                cell["source"] = [] 
           
    elif command == "IMAGE_EXTRACT":
        if cell["cell_type"] == 'code': 
            cell["source"].append("\n")
            for o in  cell["outputs"]:
                i = 0
                if "data" in o and 'image/png' in o["data"] :
                    fname = "image_%s_%s.png" % (context["cell_no"],i)  
                    full_path = "%s/%s" % (context["image-folder"],fname)  
                    with open(full_path,'w') as f:
                        f.write(o["data"]["image/png"].decode("base64"))
                    i = i + 1 
                    cell["source"].append(" ![](/images/%s) \n" % fname)

                    cell["cell_type"] = "markdown"
    else:
        log("(directives-markdown): Unknown Command: %s, %s " % (command,params))
    return cell 


