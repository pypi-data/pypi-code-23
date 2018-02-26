from bs4 import BeautifulSoup 
from multiprocessing import Pool, Value, Lock
import os, json

htmlPath = ""
storyPath = ""
outputPath = ""
files = []
filesProcessed = []
val = Value('i', 0)
lock = Lock()

def get_content_and_summary(content):
               
    index = content.index("@highlight")
    highlights = content[index:index+len(content)]
    splt = highlights.split("@highlight")

    summary = ""
    for i in range(len(splt)):
        splt[i] = splt[i].strip()
        if len(splt[i]) >= 2:
            splt[i] = splt[i].replace("\n","")
            s = splt[i] + ". "
            if i == 0:
                summary = s
            else:
                summary = summary + " " + s

    return content[:index],summary

def process_file(idx):

    file = files[idx]

    fullPath = htmlPath + file
    # print(fullPath)
    data = open(fullPath,"r",encoding="latin-1")    
    soup = BeautifulSoup(data, 'html.parser')
    title = soup.find("title")    

    title = title.text.strip()
    title = title.replace(" | Daily Mail Online","")
    title = title.replace(" | Mail Online","")

    storyFilePath = storyPath + file.replace(".html",".story")
    data = open(storyFilePath,"r",encoding="utf8")
    content = data.read()
    content,summary = get_content_and_summary(content)

    out = {}
    out["title"] = title
    out["content"] = content
    out["summary"] = summary
    outPath = outputPath + file.replace(".html",".json")

    with open(outPath, 'w') as outfile:
        json.dump(out, outfile)

    with lock:
        val.value += 1
        if(val.value % 500 == 0):
            print("Finished processing",val.value,"files of",len(files),"files")

def extract(dm_html_downloads_dir,dm_stories_dir,output_dir):

    global htmlPath
    global storyPath
    global outputPath
    global files

    htmlPath = dm_html_downloads_dir
    storyPath = dm_stories_dir
    outputPath = output_dir

    files = os.listdir(htmlPath)
    print("Total files being processed",len(files))

    with Pool(5) as p:
        p.map(process_file, range(len(files)))

    print("All done.")

# example
# extract("/data/corpus/dailymail/dailymail/downloads/","/data/corpus/dailymail/dailymail/stories/","./dm_test/")