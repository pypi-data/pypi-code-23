from broth import Broth
from bz2 import BZ2Decompressor
from os.path import isfile
from re import finditer
from re import MULTILINE
from requests import get
from subprocess import call
from subprocess import check_output
from urllib.request import urlretrieve
from urllib.request import urlopen
import xml.etree.ElementTree as ET

def clean_title(title):
    return title.replace("'","\\'").replace("`","\\`").replace('"','\\"').rstrip("\\")

def download_if_necessary(url, debug=False):
    if debug: print("starting download_if_necessary with: " + url) 
    path_to_downloaded_file = "/tmp/" + url.split("/")[-1] 
    if not isfile(path_to_downloaded_file): 
        urlretrieve(url, path_to_downloaded_file) 
        print("downloaded:", url, "to", path_to_downloaded_file) 
    return path_to_downloaded_file 

def unzip_if_necessary(filepath):
    if filepath.endswith(".zip"):
        path_to_unzipped_file = filepath.rstrip(".zip")
        if not isfile(path_to_unzipped_file):
            call(["unzip", filepath, path_to_unzipped_file])
        return path_to_unzipped_file
 

def get_most_recent_available_dump(wiki="enwiki", debug=True):

    try:

        if debug: print("starting get_most_recent_available_dump")
        wiki_url = "https://dumps.wikimedia.org/" + wiki + "/"

        broth = Broth(get(wiki_url).text)
        print("broth:", type(broth))
        dumps = [a.get("href").rstrip("/") for a in broth.select("a") if not a.text.startswith("latest") and not a.text.startswith("entities") and a.get("href") != "../"]
        dumps.reverse()
        print("dumps:", dumps)

        for dump in dumps:
           jobs = get(wiki_url + dump + "/dumpstatus.json").json()['jobs']
           if jobs['geotagstable']['status'] == "done" and jobs['pagepropstable']['status'] == "done" and jobs['articlesdumprecombine']['status'] == "done":
               print("geotags dump on " + dump + " is ready")
               return dump, jobs

    except Exception as e:
        print(e)
        raise e

def run_sql(sql_statement, db_name='', debug=False):
    try:
        if debug: print("starting run_sql with:", sql_statement)
        sql_statement = sql_statement.replace('"', '\\"')
        bash_command = '''mysql -u root ''' + db_name + ''' -e "''' + sql_statement + '''"'''
        if debug: print("bash_command:", bash_command)
        output = check_output(bash_command, shell=True).decode("utf-8")
        if debug: print("output: " + output)
        # format as rows of dictionary objects
        lines = output.strip().split("\n")
        if lines:
            header = lines[0].split("\t")
            if debug: print("header:", header)
            if len(lines) > 1:
                result = [dict(zip(header, line.split("\t"))) for line in lines[1:]]
                if debug: print("result:", str(result))
                return result
    except Exception as e:
        print("[wake] run_sql caught exception " + str(e) + " while trying to run " + sql_statement)
        raise e


def get_english_wikipedia_pages(num_chunks=1000000000):
    
    ymd, jobs = get_most_recent_available_dump()
    url = "https://dumps.wikimedia.org/enwiki/" + ymd + "/enwiki-" + ymd + "-pages-articles.xml.bz2"
    print("url:", url)

    decompressor = BZ2Decompressor()
    print("decompressor:", decompressor)
    
    req = urlopen(url)
    print("req:", req)
    
    start_page = b"<page>"
    end_page = b"</page>"
    
    text = b""
    for n in range(num_chunks):
        #print("chunk")
        chunk = req.read(16 * 1024)
        if not chunk:
            break
        #print("read")
            
        text += decompressor.decompress(chunk)
        #print("text:", text)
        #with open("/tmp/output.txt", "a") as f:
            #f.write(text.decode("utf-8"))
        
        num_pages = text.count(start_page)
        #print("num_pages:", num_pages)
        for n in range(num_pages):
            
            start_page_index = text.find(start_page)
            
            if start_page_index != -1:
                
                #print("start_page_index:", start_page_index)
                #print("text:", text[:100])
                
                # dump any text before start_page
                text = text[start_page_index:]
                #print("text:", text[:100])
                
                end_page_index = text.find(end_page)
                #print("end_page_index:", end_page_index)
                
                if end_page_index != -1:
                    
                    end_page_index += len(end_page)
                    
                    page = text[:end_page_index]
                    
                    text = text[end_page_index:]
                    
                    #print("page:", page[:20], "...", page[-20:])
                    
                    parsed = ET.fromstring(page)
                    
                    yield parsed