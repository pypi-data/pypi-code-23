#-*-coding:utf-8-*-
## writers.py is part of the fastspt library
## By MW, GPLv3+, Dec. 2017
## writers.py exports file formats widespread in SPT analysis


## ==== Imports
import xml.etree.cElementTree as ElementTree

## ==== Functions
def write_trackmate(da):
    #tree = ElementTree.Element('tmx', {'version': '1.4a'})
    Tracks = ElementTree.Element('Tracks', {'lol': 'oui'})
    ElementTree.SubElement(Tracks,'header',{'adminlang': 'EN',})
    ElementTree.SubElement(Tracks,'body')

    with open('/home/maxime/Bureau/myfile.xml', 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>')
        ElementTree.ElementTree(Tracks).write(f, 'utf-8')
    
if __name__ == "__main__":
    print "Running standalone"
    write_trackmate("")
